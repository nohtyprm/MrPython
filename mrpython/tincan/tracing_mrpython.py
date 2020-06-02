import threading, os, tokenize
import hashlib, uuid, getpass
import tincan.tracing_io as io
import copy
import time, datetime
import json
import re
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Verb,
    Activity,
    Context,
    Group,
    LanguageMap,
    ActivityDefinition,
    lrs_properties,
)
from translate import tr


show_statement_details = False

def create_actor():
    student_hash = io.get_student_hash()
    student_id = "https://www.lip6.fr/mocah/invalidURI/student-number:" + student_hash
    partner_hash = io.get_partner_hash()
    partner_id = "https://www.lip6.fr/mocah/invalidURI/partner-number:" + partner_hash
    StudentAgent = Agent(openid=student_id, name="student")
    PartnerAgent = Agent(openid=partner_id, name="partner")
    AgentGroup = Group(member=[StudentAgent, PartnerAgent], name=student_hash + "||" + partner_hash)
    return AgentGroup


def update_actor():
    global actor
    actor = create_actor()


def init_id():
    """if the student number hash isn't initialized, we use the student number in the OS username.
    If the OS username is a 7 digit integer, we hash it and keep it.
    Otherwise we keep the default.
    """
    if io.get_machine_id() == "not-initialized":
        machine_id = str(uuid.getnode())
        io.modify_machine_id(machine_id)

    student_hash = io.get_student_hash()
    if student_hash == "not-initialized":
        new_hash = None
        os_username = getpass.getuser()
        if os_username.isdigit():
            student_number = int(os_username)
            modify_student_number(str(student_number), "OS-input")
            return
        io.modify_student_hash("default", "default-input")


def modify_student_number(student_number, student_context):
    """o
    :param student_number: str
    :param student_context: str
    """
    old_hash = io.get_student_hash()
    m = hashlib.sha1(str.encode(student_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        io.modify_student_hash(new_hash, student_context)
        update_actor()
        if old_hash == "default" or old_hash == "not-initialized":
            verb = "initialized"
        else:
            verb = "updated"
        send_statement(verb, "student-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": old_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new_hash": new_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": student_context})


def modify_partner_number(partner_number):
    """
    :param partner_number: str
    """
    old_hash = io.get_partner_hash()
    m = hashlib.sha1(str.encode(partner_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        io.modify_partner_hash(new_hash)
        update_actor()
        if old_hash == "not-initialized":
            verb = "initialized"
        else:
            verb = "updated"
        send_statement(verb, "partner-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": old_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new_hash": new_hash})


def check_modified_student_number(list_numbers):
    # Change the hash identifier if the user typed his student number in the form #1234567 [+ optional partner]
    if len(list_numbers) >= 2 and list_numbers[0] == "#":
        list_numbers = list_numbers[1:]  # Remove the #
        list_numbers.strip()
        list_numbers = list_numbers.split()
        if len(list_numbers) == 1:
            student_number = list_numbers[0]
            if student_number.isdigit():
                modify_student_number(student_number, "user-input")
        elif len(list_numbers) == 2:
            student_number = list_numbers[0]
            partner_number = list_numbers[1]
            if student_number.isdigit() and partner_number.isdigit():
                modify_student_number(student_number, "user-input")
                modify_partner_number(partner_number)


def is_function_definition(instruction):
    pattern = re.compile(r'\s*def\s+(\w+)\(', re.IGNORECASE)
    match = pattern.search(instruction)
    if match:
        function_name = match.group(1)
        return function_name
    return None

def is_exercise_declaration(instruction):
    pattern = re.compile(r'\s*#\s*ex\D*(\d+)\D+(\d+)', re.IGNORECASE)

    match = pattern.search(instruction)
    if match:
        theme_number = match.group(1)
        exercise_number = match.group(2)
        return int(theme_number), int(exercise_number)
    return None


def incoherence_found(function_name, theme_number, exercise_number):
    if function_name in function_names_context:
        context_theme_number = function_names_context[function_name]["theme-number"]
        context_exercise_number = function_names_context[function_name]["exercise-number"]
        if theme_number != context_theme_number or exercise_number != context_exercise_number:
            return context_theme_number, context_exercise_number
    return None


def check_incoherence_function_exercise(source):
    import logging
    theme_number = 0
    exercise_number = 0
    for instruction in source:
        maybe_exercise_declaration = is_exercise_declaration(instruction)
        maybe_function_def = is_function_definition(instruction)
        if maybe_exercise_declaration is not None:
            theme_number, exercise_number = maybe_exercise_declaration
        elif maybe_function_def is not None:
            function_name = maybe_function_def
            maybe_incoherence = incoherence_found(function_name, theme_number, exercise_number)
            if maybe_incoherence is not None:
                expected_theme, expected_exercise = maybe_incoherence
                if theme_number == 0 and exercise_number == 0:
                    error_message = "{} has been defined.\n" \
                                    "We expected declaration #Exercise{}.{} before but\n" \
                                    "we couldn't find it".format(function_name, expected_theme, expected_exercise)
                else:
                    error_message = "{} has been defined.\n" \
                                    "We expected declaration #Exercise{}.{} before it but\n" \
                                    "you declared #Exercise{}.{}" \
                                    "".format(function_name, expected_theme, expected_exercise,
                                              theme_number, exercise_number)
                return error_message
    return None



def student_hash_uninitialized():
    return io.get_student_hash() == "default"

def clear_stack():
    """Clear the stack of statements"""
    statement = io.get_statement()
    while statement:  # While there are statements
        statement = Statement.from_json(statement)
        if send_statement_lrs(statement):  # If the statement could have been sent to the LRS
            io.remove_statement()
            statement = io.get_statement()
        else:
            return


def user_is_typing():
    """Keep the timestamp of the last action"""
    global last_typing_timestamp
    last_typing_timestamp = time.time()

def user_is_interacting():
    global last_interacting_timestamp
    last_interacting_timestamp = time.time()


def get_action_timestamps():
    return (last_typing_timestamp, last_interacting_timestamp)


def send_statement_lrs(statement):
    try:
        response = lrs.save_statement(statement)
    except OSError as e:
        print("Tracing: Couldn't connect to the LRS: {}".format(e))
        return False
    if not response:
        print("Tracing: statement failed to save")
        return False
    elif response and not response.success:
        print("Tracing: Statement request could not be sent to the LRS: {}".format(response.data))
        return False
    else:
        print("Tracing: Statement request has been sent properly to the LRS, Statement ID is {}".format(
            response.data))
        return True


def send_statement(verb, activity, activity_extensions=None):
    """Send a statement with the verb and activity keys and the context extensions"""
    if not tracing_active:
        return
    def thread_function(statement):
        pass
        # Send statement and receive HTTP response
        if not send_statement_lrs(statement):
            io.add_statement(statement)
    #Create the statement from the actor, verb, object and potentially the context
    if verb not in verbs:
        print("Tracing: Missing verb key {}".format(verb))
        return
    if activity not in activities:
        print("Tracing: Missing activity key {}".format(activity))
        return
    if send_to_LRS:
        print("Tracing: Creating and Sending statement, {} {}".format(verb, activity))
    else:
        print("Tracing: Creating (without sending) statement, {} {}".format(verb, activity))
    verb = verbs[verb]
    object = activities[activity]
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session-id": session,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/context": io.get_student_context()}
    context = Context(extensions=extensions)

    if activity_extensions:
        object = copy.deepcopy(object)
        object.definition.extensions = activity_extensions

    statement = Statement(
        actor=actor,
        verb=verb,
        object=object,
        context=context,
        timestamp=datetime.datetime.now()
    )
    if show_statement_details:
        for k, v in json.loads(statement.to_json()).items():
            print(k,v)
    # Send the statement from another thread
    if send_to_LRS:
        x = threading.Thread(target=thread_function, args=(statement,))
        x.start()



def send_statement_open_app():
    global time_opened
    time_opened = time.time()
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session": session,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/machine": io.get_machine_id()}
    send_statement("opened", "application", {})


def send_statement_close_app():
    elapsed_seconds = int(time.time() - time_opened)
    m, s = divmod(elapsed_seconds, 60)
    h, m = divmod(m, 60)
    if m < 10:
        m = "0" + str(m)
    if s < 10:
        s = "0" + str(s)
    elapsed_time = "{}:{}:{}".format(h, m, s)
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session-id": session,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/elapsed_time": elapsed_time}
    send_statement("closed", "application")


def add_extensions_error(error, error_category, filename = None, instruction = None):
    try:
        groups = error_groups[error.class_name]
    except KeyError:
        groups = "No first group"
    if "&" in groups:
        first_group, second_group = groups.split("&")
    else:
        first_group = groups
        second_group = "No second group"
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/severity": error.severity,  # warning or error
                  "https://www.lip6.fr/mocah/invalidURI/extensions/type": error.err_type,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/category": error_category,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/class": error.class_name,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/message": error.error_details(),
                  "https://www.lip6.fr/mocah/invalidURI/extensions/instruction": instruction,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/line": error.line,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/first-group": first_group,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/second-group": second_group,
                  }
    if filename:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/filename"] = os.path.basename(filename)
    return extensions


def send_statement_execute(report, mode, filename):
    """Create and send a statement at the end of the execution of the students program"""
    with tokenize.open(filename) as fp:
        source = fp.read()
        source = source.split('\n')
    # Send statements for all errors
    nb_errors = 0
    nb_warnings = 0
    for error in report.convention_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "execution-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "execution-warning"
        else:
            continue
        if error.line:
            instruction = source[error.line-1]
        else:
            instruction = "None"
        extensions = add_extensions_error(error, "convention", filename, instruction)
        send_statement("received", activity, activity_extensions=extensions)

    for error in report.compilation_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "execution-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "execution-warning"
        else:
            continue
        if error.line:
            instruction = source[error.line-1]
        else:
            instruction = "None"
        extensions = add_extensions_error(error, "compilation", filename, instruction)
        send_statement("received", activity, activity_extensions=extensions)

    for error in report.execution_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "execution-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "execution-warning"
        else:
            continue
        if error.line:
            instruction = source[error.line-1]
        else:
            instruction = "None"
        extensions = add_extensions_error(error, "execution", filename, instruction)
        send_statement("received", "execution-error", activity_extensions=extensions)

    #  Send final statement: Execution passed or failed
    if nb_errors == 0:
        verb = "passed"
    else:
        verb = "failed"
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/mode": mode,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/filename": os.path.basename(filename),
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-errors": nb_errors,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-warnings": nb_warnings}
    if not (report.has_compilation_error() or report.has_execution_error()) and mode == tr("student") and report.nb_defined_funs > 0:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/number-asserts"] = report.nb_passed_tests
    else:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/number-asserts"] = "unchecked"
    send_statement(verb, "execution", activity_extensions=extensions)


def send_statement_evaluate(report, mode, instruction):
    """Create and send a statement at the end of the execution of the students program"""
    # Send statements for all errors
    nb_errors = 0
    nb_warnings = 0
    for error in report.convention_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "evaluation-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "evaluation-warning"
        else:
            continue
        extensions = add_extensions_error(error, "convention", instruction=instruction)
        send_statement("received", activity, activity_extensions=extensions)

    for error in report.compilation_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "evaluation-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "evaluation-warning"
        else:
            continue
        extensions = add_extensions_error(error, "compilation", instruction=instruction)
        send_statement("received", activity, activity_extensions=extensions)

    for error in report.execution_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "evaluation-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "evaluation-warning"
        else:
            continue
        extensions = add_extensions_error(error, "execution", instruction=instruction)
        send_statement("received", activity, activity_extensions=extensions)


    #  Send final statement: Evaluation passed or failed
    if nb_errors == 0:
        verb = "passed"
    else:
        verb = "failed"
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/mode": mode,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/instruction": instruction,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-errors": nb_errors,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-warnings": nb_warnings}
    send_statement(verb, "evaluation", activity_extensions=extensions)


lrs = RemoteLRS(
    version=lrs_properties.version,
    endpoint=lrs_properties.endpoint,
    username=lrs_properties.username,
    password=lrs_properties.password)
init_id()
actor = create_actor()
session = str(uuid.uuid4())[:10]
verbs = {
    "opened": Verb(
        id="http://activitystrea.ms/schema/1.0/open", display=LanguageMap({'en-US': 'opened'})),
    "closed": Verb(
        id="http://activitystrea.ms/schema/1.0/close", display=LanguageMap({'en-US': 'closed'})),
    "initialized": Verb(
        id="http://activitystrea.ms/schema/1.0/initialized", display=LanguageMap({'en-US': 'initialized'})),
    "updated": Verb(
        id="http://activitystrea.ms/schema/1.0/update", display=LanguageMap({'en-US': 'updated'})),
    "created": Verb(
        id="http://activitystrea.ms/schema/1.0/create", display=LanguageMap({'en-US': 'created'})),
    "saved": Verb(
        id="http://activitystrea.ms/schema/1.0/save", display=LanguageMap({'en-US': 'saved'})),
    "saved-as": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/save-as", display=LanguageMap({'en-US': 'saved as'})),
    "switched": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/switched", display=LanguageMap({'en-US': 'switched'})),
    "started": Verb(
        id="http://activitystrea.ms/schema/1.0/start", display=LanguageMap({'en-US': 'started'})),
    "passed": Verb(
        id="http://adlnet.gov/expapi/verbs/passed", display=LanguageMap({'en-US': 'passed'})),
    "failed": Verb(
        id="http://adlnet.gov/expapi/verbs/failed", display=LanguageMap({'en-US': 'failed'})),
    "terminated": Verb(
        id="http://activitystrea.ms/schema/1.0/terminate", display=LanguageMap({'en-US': 'terminated'})),
    "received": Verb(
        id="http://activitystrea.ms/schema/1.0/receive", display=LanguageMap({'en-US': 'received'})),
    "copied": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/copied", display=LanguageMap({'en-US': 'copied'})),
    "typed": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/typed", display=LanguageMap({'en-US': 'typed'})),
    "modified": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/modified", display=LanguageMap({'en-US': 'modified'})),
    "deleted": Verb(
        id="http://activitystrea.ms/schema/1.0/delete", display=LanguageMap({'en-US': 'deleted'})),
    "inserted": Verb(
        id="http://activitystrea.ms/schema/1.0/insert", display=LanguageMap({'en-US': 'inserted'})),
    "entered": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/entered", display=LanguageMap({'en-US': 'entered'})),
    "undid": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/undid", display=LanguageMap({'en-US': 'undid'})),
    "redid": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/redid", display=LanguageMap({'en-US': 'redid'})),
    }

activities = {
    "application": Activity(
        id="http://activitystrea.ms/schema/1.0/application",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the MrPython application'}))),
    "student-number": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/student-number",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'his/her student number'}))),
    "partner-number": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/partner-number",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'his/her partners student number'}))),
    "file": Activity(
        id="http://activitystrea.ms/schema/1.0/file",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the student\'s editor file'}))),
    "mode": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/mode",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the programming mode'}),
            description=LanguageMap({'en-US': 'student/expert mode in MrPython'}))),
    "execution": Activity(
            id="https://www.lip6.fr/mocah/invalidURI/activity-types/execution",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'a programming execution'}),
                description=LanguageMap({'en-US': 'execution of the student\'s editor'}))),
    "evaluation": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/interpretation",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming evaluation'}),
            description=LanguageMap({'en-US': 'interpretation made by the MrPython interpretor'}))),
    "execution-error": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/execution-error",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an execution error'}))),
    "execution-warning": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/execution-warning",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an execution warning'}))),
    "evaluation-error": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation-error",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an evaluation error'}))),
    "evaluation-warning": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation-warning",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an evaluation warning'}))),
    "output-console": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/output-console",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the output console of MrPython'}))),
    "keyword": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/keyword",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a keyword'}))),
    "line": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/line",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming line'}))),
    "sequence": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/sequence",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a sequence of instructions'}))),
    "text": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/text",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'some text'}))),
    "typing-state": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/typing-state",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a typing state'}))),
    "interacting-state": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/interacting-state",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an interacting state'}))),
    "idle-state": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/idle-state",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an idle state'}))),

    }

with open(os.path.join(os.path.dirname(__file__), "tracing_config.json"))as file:
    config = json.load(file)
    tracing_active = config["tracing_active"]
    send_to_LRS = config["send_to_LRS"]
    error_groups = config["error_groups"]
    function_names_context = config["exercises_functions"]

last_typing_timestamp = None
last_interacting_timestamp = None
