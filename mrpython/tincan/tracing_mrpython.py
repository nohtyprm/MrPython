import threading
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

lrs = RemoteLRS(
    version=lrs_properties.version,
    endpoint=lrs_properties.endpoint,
    username=lrs_properties.username,
    password=lrs_properties.password)
actor = Agent(name='AdilPython0.0.0', mbox='mailto:tincanpython@tincanapi.com')

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
    "terminated": Verb(
        id="http://activitystrea.ms/schema/1.0/terminate", display=LanguageMap({'en-US': 'terminated'})),
    "failed": Verb(
            id="http://adlnet.gov/expapi/verbs/failed", display=LanguageMap({'en-US': 'failed'})),
    "passed": Verb(
        id="http://adlnet.gov/expapi/verbs/passed", display=LanguageMap({'en-US': 'passed'})),
    }
activities = {
    "application": Activity(
        id="http://activitystrea.ms/schema/1.0/application",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'an application'}),
            description=LanguageMap({'en-US': 'the MrPython application'}))),
    "file": Activity(
        id="http://activitystrea.ms/schema/1.0/file",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming file'}),
            description=LanguageMap({'en-US': 'new MrPython file'}))),
    "mode": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/mode",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the programming mode'}),
            description=LanguageMap({'en-US': 'student/expert mode in MrPython'}))),
    "function": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/function",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming function'}))),
    "interpreter": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/interpreter",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming interpreter'}),
            description=LanguageMap({'en-US': 'the interpreter present in MrPython'}))),
    "execution": Activity(
            id="https://www.lip6.fr/mocah/invalidURI/activity-types/execution",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'an execution'}),
                description=LanguageMap({'en-US': 'execution of the student program'}))),
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
    }


def send_statement(verb, activity):
    """Send a statement with the verb and activity keys"""
    def thread_function(verb, activity):
        if verb not in verbs:
            print("Tracing: Missing key {}".format(verb))
            return
        if activity not in activities:
            print("Tracing: Missing key {}".format(activity))
            return
        print("Tracing: Creating and Sending statement, {} {}".format(verb,activity))
        verb = verbs[verb]
        object = activities[activity]
        # print("constructing the Statement...")
        statement = Statement(
            actor=actor,
            verb=verb,
            object=object
        )

        # print("saving the Statement...")
        '''
        response = lrs.save_statement(statement)
        if not response:
            print("Tracing: statement failed to save")
        if response.success:
            print("Tracing: Statement request has been sent properly to the LRS, Statement ID is {}".format(response.data))
        else:
            print("Tracing: Statement request could not been sent to the LRS: {}".format(response.data))
        '''

    x = threading.Thread(target=thread_function, args=(verb, activity))
    x.start()

def send_statement_from_report(report,mode):
    """Create and send a statement of the execution of the students program"""
    compil_fail = False
    exec_fail = False
    conv_fail = False
    warning = False
    #Detect compilation errors
    if report.has_compilation_error():
        compil_fail = True
    if report.has_execution_error():
        exec_fail = True

    for error in report.convention_errors:
        if error.severity == "error":
            conv_fail = True
        elif error.severity == "warning":
            warning = True

    if compil_fail:
        send_statement("failed", "error-compilation")
    elif exec_fail:
        send_statement("failed", "error-execution")
    elif conv_fail:
        send_statement("failed", "error-convention")
    elif warning:
        send_statement("failed", "error-warning")
    elif mode == "eval":
        send_statement("passed", "interpreter")
    else:
        send_statement("passed", "execution")
