import threading, copy, os
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
#LRS server
lrs = RemoteLRS(
    version=lrs_properties.version,
    endpoint=lrs_properties.endpoint,
    username=lrs_properties.username,
    password=lrs_properties.password)
actor = Agent(name='AdilPython0.0.0', mbox='mailto:tincanpython@tincanapi.com')
#Dictionary xAPI verbs
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
    "had": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/had", display=LanguageMap({'en-US': 'had'})),
    "completed": Verb(
        id="http://activitystrea.ms/schema/1.0/complete", display=LanguageMap({'en-US': 'completed'})),
    }
#Dictionary xAPI activities
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
    "function": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/function",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming function'}))),
    }


def send_statement(verb, activity, extensions={}):
    """Send a statement with the verb and activity keys"""
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
        context = Context(extensions=extensions) if extensions else None  # Context is optional

        if context:
            #print(context.to_json())
            statement = Statement(
                actor=actor,
                verb=verb,
                object=object,
                context=context
            )
        else:
            statement = Statement(
                actor=actor,
                verb=verb,
                object=object
            )
        '''
        # Send statement and receive HTTP response
        response = lrs.save_statement(statement)
        if not response:
            print("Tracing: statement failed to save")
        if response.success:
            print("Tracing: Statement request has been sent properly to the LRS, Statement ID is {}".format(response.data))
        else:
            print("Tracing: Statement request could not been sent to the LRS: {}".format(response.data))
        '''
    # Send the statement from another thread
    #x = threading.Thread(target=thread_function, args=(verb, activity))
    #x.start()


def send_statement_from_report(report, command, mode, instruction=None, filename=None):
    """Create and send a statement at the end of the execution of the students program"""
    compile_fail = False
    exec_fail = False
    conv_fail = False
    warning = False
    #Detect errors and type of errors
    if report.has_compilation_error():
        compile_fail = True
    if report.has_execution_error():
        exec_fail = True
    for error in report.convention_errors:
        if error.severity == "error":
            conv_fail = True
        elif error.severity == "warning":
            warning = True

    # Send different statements for different errors
    verb = None
    activity = None
    if compile_fail:
        verb = "had"
        activity = "error-compilation"
    elif exec_fail:
        verb = "had"
        activity = "error-execution"
    elif conv_fail:
        verb = "had"
        activity = "error-convention"
    elif warning:
        verb = "had"
        activity = "error-warning"
    elif command == "eval":
        verb = "completed"
        activity = "interpretation"
    else:
        verb = "completed"
        activity = "execution"

    # Add extensions
    extensions = {}
    extensions["https://www.lip6.fr/mocah/invalidURI/extensions/mode"] = mode # Expert or student
    if command == "eval":  # If the user is using the interpreter, we send the instruction typed
        if instruction:
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/instruction"] = instruction
    else:  # If the user is executing his program, we add the filename and the number of asserts made if mode = student
        if filename:
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/filename"] = os.path.basename(filename)
        if command == "exec" and tr(mode) == tr("student"):
            extensions["https://www.lip6.fr/mocah/invalidURI/extensions/number-asserts"] = report.nb_passed_tests
    send_statement(verb, activity, extensions=extensions)


def test_function():
    return

if __name__ == "__main__":
    test_function()
