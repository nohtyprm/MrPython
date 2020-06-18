import threading, os, tokenize
import hashlib, uuid, getpass
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
    tracing_config as config,
    tracing_io as io
)
from translate import tr


def create_actor():
    student_id = "https://www.lip6.fr/mocah/invalidURI/student-number:" + student_hash
    partner_id = "https://www.lip6.fr/mocah/invalidURI/partner-number:" + partner_hash
    StudentAgent = Agent(openid=student_id, name="student")
    PartnerAgent = Agent(openid=partner_id, name="partner")
    AgentGroup = Group(member=[StudentAgent, PartnerAgent], name=student_hash + "||" + partner_hash)
    print(student_hash, partner_hash)
    return AgentGroup


def update_actor():
    global actor
    actor = create_actor()


def init_id():
    """
    If the OS username is a digit integer, we hash it and use it to identify the user in the statements.
    We also identify the computer used with the hashed MAC Address
    :return:
    """
    machine_id = str(uuid.getnode())
    student_hash = "default"
    partner_hash = "default"
    input_type = "default-input"
    os_username = getpass.getuser()
    if os_username.isdigit():
        m = hashlib.sha1(str.encode(os_username))
        student_hash = m.hexdigest()[:10]
        input_type = "OS-input"
        send_statement("initialized", "student-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": "default",
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new-hash": student_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": input_type})
    return machine_id, student_hash, partner_hash, input_type


def modify_student_number(student_number):
    """o
    :param student_number: str
    :param student_context: str
    """
    global student_hash, input_type
    old_hash = student_hash
    m = hashlib.sha1(str.encode(student_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        student_hash = new_hash
        input_type = "user-input"
        update_actor()
        if old_hash == "default":
            verb = "initialized"
        else:
            verb = "updated"
        send_statement(verb, "student-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": old_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new-hash": new_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": input_type})


def modify_partner_number(partner_number):
    """
    :param partner_number: str
    """
    global partner_hash, input_type
    old_hash = partner_hash
    m = hashlib.sha1(str.encode(partner_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        partner_hash = new_hash
        input_type = "user-input"
        update_actor()
        if old_hash == "default":
            verb = "initialized"
        else:
            verb = "updated"
        send_statement(verb, "partner-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": old_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new-hash": new_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": input_type})


def check_modified_student_number(list_numbers):
    """
    Change the hash identifier if the user type one (or two) integers in the form # student_number [partner_number]
    Called in PyEditor and StudentRunner to check the first line of the editor
    """
    pattern = re.compile(r'\s*#\s*(\d+)(\s+\d*)?', re.IGNORECASE)
    match = pattern.search(list_numbers)
    if match:
        student_number = match.group(1)
        partner_number = match.group(2)
        modify_student_number(student_number)
        if partner_number:
            modify_partner_number(partner_number)


def is_function_definition(instruction):
    pattern = re.compile(r'\s*def\s+(\w+)\(', re.IGNORECASE)
    match = pattern.match(instruction)
    if match:
        function_name = match.group(1)
        return function_name
    return None

def is_exercise_declaration(instruction):
    pattern = re.compile(r'\s*#\s*ex\D*(\d+)\D+(\d+)', re.IGNORECASE)

    match = pattern.match(instruction)
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
    theme_number = None
    exercise_number = None
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
                if theme_number is None and exercise_number is None:
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
    return student_hash == "default"

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


def save_execution_start():
    """Keep the timestamp of the last action"""
    global start_execution_timestamp
    start_execution_timestamp = time.time()


def get_action_timestamps():
    return (last_typing_timestamp, last_interacting_timestamp)

def execution_duration():
    return time.time() - start_execution_timestamp

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


def send_statement(verb_key, activity_key, activity_extensions=None):
    """Send a statement with the verb and activity keys and the context extensions"""
    global statement_number
    if not tracing_active:
        return
    def thread_function(statement):
        pass
        # Send statement and receive HTTP response
        if not send_statement_lrs(statement):
            io.add_statement(statement)
    #Create the statement from the actor, verb, object and potentially the context
    if verb_key not in verbs:
        print("Tracing: Missing verb key {}".format(verb_key))
        return
    if activity_key not in activities:
        print("Tracing: Missing activity key {}".format(activity_key))
        return
    if send_to_LRS:
        print("Tracing: Creating and Sending statement {}, {} {}".format(statement_number, verb_key, activity_key))
    else:
        print("Tracing: Creating (without sending) statement {}, {} {}".format(statement_number, verb_key, activity_key))
    verb = verbs[verb_key]
    activity = activities[activity_key]
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session-id": session,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/machine-id": machine_id,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": input_type}
    context = Context(extensions=extensions)

    if activity_extensions:
        activity = copy.deepcopy(activity)
        activity.definition.extensions = activity_extensions

    statement_time = datetime.datetime.utcnow()
    statement_time = statement_time.replace(tzinfo=datetime.timezone.utc)
    statement = Statement(
        actor=actor,
        verb=verb,
        object=activity,
        context=context,
        timestamp=statement_time
    )
    if debug_log:
        data = json.loads(statement.to_json())
        with open(debug_filepath, "a") as f:
            f.write("STATEMENT " + str(statement_number) + "\n")
            json.dump(data, f, indent=2)
            f.write("\n")
    statement_number += 1
    # Send the statement from another thread
    if send_to_LRS:
        x = threading.Thread(target=thread_function, args=(statement,))
        x.start()



def send_statement_open_app():
    global time_opened, session
    # Initialize session
    if not os.path.isfile(session_filepath):
        session = str(uuid.uuid4())[:10]
        with open(session_filepath, "w") as f:
            f.write(session)
    else:
        with open(session_filepath, "r") as f:
            session = f.read()
    #Initialize debug
    if debug_log:
        file = open(debug_filepath, "w")  # Erase previous content
        file.close()
        print("Debug log enabled: All statements are kept in " + debug_filepath)
    time_opened = time.time()
    send_statement("opened", "application")


def send_statement_close_app():
    elapsed_seconds = int(time.time() - time_opened)
    m, s = divmod(elapsed_seconds, 60)
    h, m = divmod(m, 60)
    if m < 10:
        m = "0" + str(m)
    if s < 10:
        s = "0" + str(s)
    elapsed_time = "{}:{}:{}".format(h, m, s)
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session": session,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/elapsed-time": elapsed_time}
    send_statement("closed", "application", extensions)
    os.remove(session_filepath)


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
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/nb-asserts"] = report.nb_passed_tests
    else:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/nb-asserts"] = "unchecked"
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


statement_number = 1 # for debug

# global variables used to keep tracing information
machine_id, student_hash, partner_hash, input_type = init_id()
session = None  # Initialized in send_statement_open_app()
tracing_active = config.tracing_active
send_to_LRS = config.send_to_LRS
debug_log = config.debug_log
debug_filepath = config.debug_filepath
error_groups = config.error_groups
function_names_context = config.function_names_context
last_typing_timestamp = None
last_interacting_timestamp = None
start_execution_timestamp = None

# xAPI setup
lrs = RemoteLRS(
    version=config.lrs_version,
    endpoint=config.lrs_endpoint,
    username=config.lrs_username,
    password=config.lrs_password)
actor = create_actor()
verbs = config.verbs
activities = config.activities

session_filepath = config.session_filepath

