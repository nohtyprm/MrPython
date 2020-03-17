import threading, os
import hashlib, uuid, getpass
import tincan.tracing_io as io
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Verb,
    Activity,
    Context,
    Result,
    LanguageMap,
    ActivityDefinition,
    StateDocument,
    lrs_properties,
)
from translate import tr


def init_student_number():
    """if the student number hash isn't initialized, we use the student number in the OS username.
    If the OS username is a 7 digit integer, we hash it and keep it.
    Otherwise we keep the default.
    """
    student_hash = io.get_student_hash()
    if student_hash == "not-initialized":
        new_hash = None
        os_username = getpass.getuser()
        os_username = "1234367" #Test
        if os_username.isnumeric():
            student_number = int(os_username)
            if student_number > 1000000 and student_number < 10000000:
                modify_student_number(str(student_number))
                return
        io.modify_student_hash("default")


def modify_student_number(student_number):
    """
    Keep a hash of the student number
    """
    m = hashlib.sha1(str.encode(student_number))
    student_hash = m.hexdigest()[:10]
    io.modify_student_hash(student_hash)


def create_actor():
    student_hash = io.get_student_hash()
    student_id = "https://www.lip6.fr/mocah/invalidURI/student-number:" + student_hash
    return Agent(openid=student_id, name=student_hash)


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


def send_statement(verb, activity, extensions={}):
    """Send a statement with the verb and activity keys and the context extensions"""
    def thread_function(verb, activity):
        #Create the statement from the actor, verb, object and potentially the context
        if verb not in verbs:
            print("Tracing: Missing key {}".format(verb))
            return
        if activity not in activities:
            print("Tracing: Missing key {}".format(activity))
            return
        print("Tracing: Creating and Sending statement, {} {}".format(verb, activity))
        verb = verbs[verb]
        object = activities[activity]
        extensions["https://www.lip6.fr/mocah/invalidURI/extensions/session:"] = session
        context = Context(extensions=extensions)

        statement = Statement(
            actor=actor,
            verb=verb,
            object=object,
            context=context
        )
        # Send statement and receive HTTP response
        if not send_statement_lrs(statement):
            io.add_statement(statement)

    # Send the statement from another thread
    x = threading.Thread(target=thread_function, args=(verb, activity))
    x.start()


def send_statement_from_report(report, command, mode, instruction=None, filename=None):
    """Create and send a statement at the end of the execution of the students program"""
    # Send statements for all errors
    success = True
    for error in report.convention_errors:
        if error.severity == "warning" or error.severity == "error":
            activity = "error-convention" if error.severity == "error" else "error-warning"
            extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/error-details": error.error_details()}
            send_statement("had", activity, extensions)
            success = False
    for error in report.compilation_errors:
        extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/error-details": error.error_details()}
        send_statement("had", "error-compilation", extensions)
        success = False
    for error in report.execution_errors:
        extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/error-details": error.error_details()}
        send_statement("had", "error-execution", extensions)
        success = False
    #  Check if the student tested his functions
    print(report.nb_passed_tests)
    if report.nb_passed_tests == 1:
        extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/error-details": tr("Only one (successful) test found, it's probably not enough")}
        send_statement("had", "error-warning", extensions)
    elif report.nb_passed_tests == 0:
        extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/error-details": tr("There is no test! you have to write tests!")}
        send_statement("had", "error-convention", extensions)
    # Send statement final report
    if success:
        verb = "passed"
    else:
        verb = "failed"
    if command == "eval":
        activity = "interpretation"
    else:
        activity = "execution"

    extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/mode": mode}
    if command == "eval":  # If the user is using the interpreter, we send the instruction typed
        if instruction:
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/instruction"] = instruction
    else:  # If the user is executing his program, we add the filename and the number of asserts made if mode = student
        if filename:
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/filename"] = os.path.basename(filename)
        if command == "exec" and tr(mode) == tr("student"):
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/number-asserts"] = report.nb_passed_tests
    #  Final statement: Execution passed or failed
    send_statement(verb, activity, extensions)


lrs = RemoteLRS(
    version=lrs_properties.version,
    endpoint=lrs_properties.endpoint,
    username=lrs_properties.username,
    password=lrs_properties.password)
init_student_number()
actor = create_actor()
session = str(uuid.uuid4())[:10]
verbs = {
    "created": Verb(
        id="http://activitystrea.ms/schema/1.0/create", display=LanguageMap({'en-US': 'created'})),
    "opened": Verb(
        id="http://activitystrea.ms/schema/1.0/open", display=LanguageMap({'en-US': 'opened'})),
    "closed": Verb(
        id="http://activitystrea.ms/schema/1.0/close", display=LanguageMap({'en-US': 'closed'})),
    "saved": Verb(
        id="http://activitystrea.ms/schema/1.0/save", display=LanguageMap({'en-US': 'saved'})),
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
    "had": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/had", display=LanguageMap({'en-US': 'had'})),
    "typed": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/typed", display=LanguageMap({'en-US': 'typed'})),
    }

activities = {
    "application": Activity(
        id="http://activitystrea.ms/schema/1.0/application",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the MrPython application'}))),
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
    "interpretation": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/interpretation",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming interpretation'}),
            description=LanguageMap({'en-US': 'interpretation made by the MrPython interpretor'}))),
    "error-compilation": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/error-compilation",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a compilation error'}))),
    "error-execution": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/error-execution",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an execution error'}))),
    "error-convention": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/error-convention",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a convention error'}))),
    "error-warning": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/error-warning",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a warning error'}))),
    "keyword": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/keyword",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a keyword'}))),
    }

if __name__ == "__main__":
    '''
    verb = verbs["opened"]
    object = activities["application"]

    statement = Statement(
        actor=actor,
        verb=verb,
        object=object,
    )
    # Send statement and receive HTTP response
    io.add_statement(statement)
    '''
    clear_stack()