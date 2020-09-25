"""
Main module in charge of tracing.
Manage the creation and sending of statements,
"""
import threading, os, tokenize
import hashlib, uuid, getpass
import copy
import time, datetime
import re
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Context,
    Group,
    tracing_config as config,
    tracing_io as io
)
from translate import tr


def _create_actor():
    """Create xAPI actor"""
    student_id = "https://www.lip6.fr/mocah/invalidURI/student-number:" + student_hash
    partner_id = "https://www.lip6.fr/mocah/invalidURI/partner-number:" + partner_hash
    StudentAgent = Agent(openid=student_id, name="student")
    PartnerAgent = Agent(openid=partner_id, name="partner")
    AgentGroup = Group(member=[StudentAgent, PartnerAgent], name=student_hash + "||" + partner_hash)
    # print(student_hash, partner_hash)
    return AgentGroup


def _update_actor():
    global actor
    actor = _create_actor()


def _init_id():
    """
    If the OS username is a digit integer, we hash it and use it to identify the user in the statements.
    We also identify the computer used with the hashed MAC Address
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


def _modify_student_number(student_number):
    """
    Check if hashed student_number is different than the current kept hash.
    If that's the case, modify the kept hash send a statement
    :param student_number: str
    """
    global student_hash, input_type
    old_hash = student_hash
    m = hashlib.sha1(str.encode(student_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        student_hash = new_hash
        input_type = "user-input"
        _update_actor()
        if old_hash == "default":
            verb = "initialized"
        else:
            verb = "updated"
        send_statement(verb, "student-number",
                       {"https://www.lip6.fr/mocah/invalidURI/extensions/old-hash": old_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/new-hash": new_hash,
                        "https://www.lip6.fr/mocah/invalidURI/extensions/input-context": input_type})


def _modify_partner_number(partner_number):
    """
    Check if hashed partner_number is different than the current kept hash.
    If that's the case, modify the kept hash send a statement
    :param partner_number: str
    """
    global partner_hash, input_type
    old_hash = partner_hash
    m = hashlib.sha1(str.encode(partner_number))
    new_hash = m.hexdigest()[:10]
    if old_hash != new_hash:
        partner_hash = new_hash
        input_type = "user-input"
        _update_actor()
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
    Change the hash identifiers if the user typed one (or two) integers in the form # student_number partner_number
    Called in PyEditor and Console to check the first line of the editor.
    """
    pattern = re.compile(r'\s*#\s*(\d+)(\s+\d*)?', re.IGNORECASE)
    match = pattern.search(list_numbers)
    if match:
        student_number = match.group(1)
        partner_number = match.group(2)
        _modify_student_number(student_number)
        if partner_number:
            _modify_partner_number(partner_number)


def _is_function_definition(instruction):
    pattern = re.compile(r'\s*def\s+(\w+)\(', re.IGNORECASE)
    match = pattern.match(instruction)
    if match:
        function_name = match.group(1)
        return function_name
    return None


def _is_exercise_declaration(instruction):
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
    # Check if there is an incoherence in the user's source code: Exercise declared != Function name
    theme_number = None
    exercise_number = None
    for instruction in source:
        maybe_exercise_declaration = _is_exercise_declaration(instruction)
        maybe_function_def = _is_function_definition(instruction)
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
    """Re-send and clear the stack of statements that couldn't be sent."""
    def thread_function(stack):
        for i in range(len(stack)):
            s = stack[i]
            statement = Statement.from_json(s)
            if debug_log_print:
                print("Tracing: Sending statement number {} from stack".format(i+1))
            if not _send_statement_lrs(statement):  # Send statement and receive HTTP response
                io.add_statement(statement)  # Backup the statement if it couldn't been sent
    stack = io.get_and_clear_stack()
    if stack is not None:
        x = threading.Thread(target=thread_function, args=(stack,))  # Non-blocking
        x.start()


def user_is_typing():
    """Keep the timestamp of the last action"""
    global last_typing_timestamp
    last_typing_timestamp = time.time()


def user_is_interacting():
    """Keep the timestamp of the last interaction"""
    global last_interacting_timestamp
    last_interacting_timestamp = time.time()


def save_execution_start():
    """Keep the timestamp of the the start of a program's execution."""
    global start_execution_timestamp
    start_execution_timestamp = time.time()


def get_action_timestamps():
    return last_typing_timestamp, last_interacting_timestamp


def execution_duration():
    """ Get the duration of a program's execution. Used after save_execution_start()"""
    return time.time() - start_execution_timestamp


def update_active_timestamp():
    """Update last active timestamp of the user's session. Used to know when to change session ID"""
    io.write_session_info(session_id, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), tracing_enabled)


def _send_statement_lrs(statement):
    """Send statement to the LRS"""
    try:
        response = lrs.save_statement(statement)
    except OSError as e:
        if debug_log_print:
            print("Tracing: Couldn't connect to the LRS: {}".format(e))
        return False
    if not response:
        if debug_log_print:
            print("Tracing: Failed to get server response for statement request")
        return False
    elif response and not response.success:
        if debug_log_print:
            print("Tracing: Statement request could not be sent to the LRS: {}".format(response.data))
        return False
    else:
        if debug_log_print:
            print("Tracing: Statement request has been sent properly to the LRS, Statement ID is {}".format(
            response.data))
        return True


def send_statement(verb_key, activity_key, activity_extensions=None):
    """Send a statement with the verb and activity keys and the context extensions"""
    if not tracing_enabled:
        return

    def thread_function(statement):
        # Send statement and receive HTTP response
        if not _send_statement_lrs(statement):
            io.add_statement(statement) # Backup the statement if it couldn't been sent

    global statement_number
    # Create the statement from the actor, the verb, the context and the activity keys
    if verb_key not in verbs:
        if debug_log_print:
            print("Tracing: Missing verb key {}".format(verb_key))
        return
    if activity_key not in activities:
        if debug_log_print:
            print("Tracing: Missing activity key {}".format(activity_key))
        return
    if send_to_LRS and debug_log_print:
        print("Tracing: Creating and Sending statement {}, {} {}".format(statement_number, verb_key, activity_key))
    elif debug_log_print:
        print("Tracing: Creating (without sending) statement {}, {} {}".format(statement_number, verb_key, activity_key))
    verb = verbs[verb_key]
    activity = activities[activity_key]
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/session-id": session_id,
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
    if debug_log_print:
        io.add_statement_debug(statement, statement_number)
    statement_number += 1
    # Send the statement from another thread
    if send_to_LRS:
        x = threading.Thread(target=thread_function, args=(statement,))
        x.start()


def user_first_session():
    """Check if it's the user's first session by checking if the session file exists.
    Used to ask initial consent for tracing"""
    return not io.session_file_exists()


def check_tracing_is_enabled():
    _, _, tracing_enabled = io.get_session_info()
    return tracing_enabled

def switch_tracing_enabled_disabled():
    """Enable/disable tracing"""
    global tracing_enabled
    prev_session, prev_active_time, tracing_enabled = io.get_session_info()
    if tracing_enabled:
        #  User disabled tracing.
        #  We assume it's ok to send this statement since the user initially enabled the tracing before the switch
        send_statement("disabled", "tracing")
    tracing_enabled = not tracing_enabled
    if tracing_enabled:
        send_statement("enabled", "tracing")
    io.write_session_info(prev_session, prev_active_time, tracing_enabled)
    return tracing_enabled

def initialize_tracing(user_enabled_tracing):
    """Initialize the session file, the debug file and global variables"""
    global opened_timestamp, session_id, tracing_enabled  # Initialize global vars
    rewrite_session_id = False
    initially_accepted_tracing = False  # User said yes in the initial tracing message box

    # Initialize Session

    if io.session_file_exists():
        session_id, last_active_time, _ = io.get_session_info()
        last_active_time = datetime.datetime.strptime(last_active_time, "%Y-%m-%dT%H:%M:%S")
        elapsed_time = datetime.datetime.now() - last_active_time
        if elapsed_time > datetime.timedelta(minutes=30):  # If the last session's end was less than 30 minutes before
            rewrite_session_id = True
    else:
        if user_enabled_tracing:  # If it's the first session and user accepted tracing
            initially_accepted_tracing = True
        rewrite_session_id = True

    if rewrite_session_id:
        session_id = str(uuid.uuid1(clock_seq=int(time.time() * 1e9)))
    active_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    tracing_enabled = user_enabled_tracing
    io.write_session_info(session_id, active_time, tracing_enabled)  # write session file

    # Initialize debug

    if debug_log_print:
        io.initialize_debug_file()
    opened_timestamp = time.time()

    # Clear the stack

    if tracing_enabled:
        clear_stack()
    
    # Send statements

    if initially_accepted_tracing:
        send_statement("accepted", "tracing")
    send_statement("opened", "application")


def send_statement_close_app():
    """Send the statement of closing of the app"""
    if not tracing_enabled:
        return
    elapsed_seconds = int(time.time() - opened_timestamp)
    m, s = divmod(elapsed_seconds, 60)
    h, m = divmod(m, 60)
    if m < 10:
        m = "0" + str(m)
    if s < 10:
        s = "0" + str(s)
    elapsed_time = "{}:{}:{}".format(h, m, s)
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/elapsed-time": elapsed_time}
    send_statement("closed", "application", extensions)


def _add_extensions_error(error, error_category, filename=None, instruction=None):
    """Add extensions to error statement"""
    try:
        groups = error_groups[error.class_name]
        class_name = error.class_name
    except KeyError:
        groups = "No first group"
        class_name = "No class name"
    if "&" in groups:
        first_group, second_group = groups.split("&")
    else:
        first_group = groups
        second_group = "No second group"
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/severity": error.severity,  # warning or error
                  "https://www.lip6.fr/mocah/invalidURI/extensions/type": error.err_type,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/category": error_category,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/class": class_name,
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
    if not tracing_enabled:
        return
    with tokenize.open(filename) as fp:
        source = fp.read()
        source = source.split('\n')
    manually_terminated = False
    nb_errors = 0
    nb_warnings = 0

    # Check and send statements for all errors

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
        extensions = _add_extensions_error(error, "convention", filename, instruction)
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
        extensions = _add_extensions_error(error, "compilation", filename, instruction)
        send_statement("received", activity, activity_extensions=extensions)

    for error in report.execution_errors:
        if error.err_type == tr("User interruption"):
            manually_terminated = True
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
        extensions = _add_extensions_error(error, "execution", filename, instruction)
        send_statement("received", "execution-error", activity_extensions=extensions)

    #  Send final statement: Execution passed or failed

    if nb_errors == 0:
        verb = "passed"
    elif manually_terminated:
        verb = "terminated"
    else:
        verb = "failed"

    with open(filename, "r") as f:
        file_length = len(f.read())
    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/mode": mode,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/filename": os.path.basename(filename),
                  "https://www.lip6.fr/mocah/invalidURI/extensions/filelength": file_length,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-errors": nb_errors,
                  "https://www.lip6.fr/mocah/invalidURI/extensions/nb-warnings": nb_warnings}
    if manually_terminated:
        t = execution_duration()
        t = str(round(t, 4)) + " seconds"
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/execution-duration"] = t
    if not (report.has_compilation_error() or report.has_execution_error()) and mode == tr("student") and \
            report.nb_defined_funs > 0:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/nb-asserts"] = report.nb_passed_tests
    else:
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/nb-asserts"] = "unchecked"
    send_statement(verb, "execution", activity_extensions=extensions)


def send_statement_evaluate(report, mode, instruction):
    """Create and send a statement at the end of the evaluation of the students instruction"""
    if not tracing_enabled:
        return
    nb_errors = 0
    nb_warnings = 0

    # Check and send statements for all errors

    for error in report.convention_errors:
        if error.severity == "error":
            nb_errors += 1
            activity = "evaluation-error"
        elif error.severity == "warning":
            nb_warnings += 1
            activity = "evaluation-warning"
        else:
            continue
        extensions = _add_extensions_error(error, "convention", instruction=instruction)
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
        extensions = _add_extensions_error(error, "compilation", instruction=instruction)
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
        extensions = _add_extensions_error(error, "execution", instruction=instruction)
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


#
# global variables used during tracing
#
statement_number = 1  # keep number order for statements
# Identifiers
machine_id, student_hash, partner_hash, input_type = _init_id()
session_id = None  # Session ID, Initialized in initialize_tracing()
# Tracing behaviour
tracing_enabled = None  # Enable user to enable/disable tracing, Initialized in initialize_tracing()
send_to_LRS = config.send_to_LRS  # Send the created statements to the LRS
debug_log_print = config.debug_log_print  # Keep Log of statements and Print messages related to tracing
# Error and function data
error_groups = config.error_groups
function_names_context = config.function_names_context
# Timestamps
opened_timestamp = None  # Opened app
last_typing_timestamp = None  # Last typed in editor
last_interacting_timestamp = None  # Last interacted with software
start_execution_timestamp = None  # Last execution start

#
# xAPI and LRS setup
#
lrs = RemoteLRS(
    version=config.lrs_version,
    endpoint=config.lrs_endpoint,
    username=config.lrs_username,
    password=config.lrs_password,
    proxy_name=config.proxy_name,
    proxy_port=config.proxy_port)
actor = _create_actor()
verbs = config.verbs
activities = config.activities
