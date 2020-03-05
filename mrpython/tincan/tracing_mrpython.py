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
        "executed": Verb(
            id="https://www.lip6.fr/mocah/invalidURI/verbs/executed", display=LanguageMap({'en-US': 'executed'})),
        "defined": Verb(
            id="http://id.tincanapi.com/verb/defined", display=LanguageMap({'en-US': 'defined'}))
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
        "program": Activity(
            id="https://www.lip6.fr/mocah/invalidURI/activity-types/program",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'a computer program'}),
                description=LanguageMap({'en-US': 'program made by the user'}))),
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
            id="interpreter https://www.lip6.fr/mocah/invalidURI/activity-types/interpreter",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'a programming interpreter'}),
                description=LanguageMap({'en-US': 'the interpreter present in MrPython'})))
    }

def send_statement(verb, activity):
    """Send a statement with the verb and activity keys"""
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