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


class TracingMrPython(object):
    def __init__(self, *args, **kwargs):
        self.lrs = RemoteLRS(
            version=lrs_properties.version,
            endpoint=lrs_properties.endpoint,
            username=lrs_properties.username,
            password=lrs_properties.password)
        self.actor = Agent(name='AdilPython0.0.0', mbox='mailto:tincanpython@tincanapi.com')
        self.verbs = self.define_verbs()  # Dictionary of all verbs
        self.activities = self.define_activities()  # Dictionary of all activities

    def send_statement(self, verb, activity):
        """Send a statement with the verb and activity keys"""
        if verb not in self.verbs:
            print("Tracing: Missing key {}".format(verb))
            return
        if activity not in self.activities:
            print("Tracing: Missing key {}".format(activity))
            return
        print("Tracing: Creating and Sending statement")
        actor = self.actor
        verb = self.verbs[verb]
        object = self.activities[activity]
        # print("constructing the Statement...")
        statement = Statement(
            actor=actor,
            verb=verb,
            object=object
        )

        # print("saving the Statement...")
        response = self.lrs.save_statement(statement)
        if not response:
            print("Tracing: statement failed to save")
        if response.success:
            print("Tracing: Statement request has been sent properly to the LRS, Statement ID is {}".format(response.data))
        else:
            print("Tracing: Statement request could not been sent to the LRS: {}".format(response.data))

    @staticmethod
    def define_verbs():
        verbs = {
            "created": Verb(
                id="http://activitystrea.ms/schema/1.0/create", display=LanguageMap({'en-US': 'created'})),
            "opened": Verb(
                id="http://activitystrea.ms/schema/1.0/open", display=LanguageMap({'en-US': 'opened'})),
            "saved": Verb(
                id="http://activitystrea.ms/schema/1.0/save", display=LanguageMap({'en-US': 'saved'})),
            "switched": Verb(
                id="https://www.lip6.fr/mocah/invalidURI/verbs/switched", display=LanguageMap({'en-US': 'switched'})),
            "executed": Verb(
                id="https://www.lip6.fr/mocah/invalidURI/verbs/executed", display=LanguageMap({'en-US': 'executed'})),
            "defined": Verb(
                id="http://id.tincanapi.com/verb/defined", display=LanguageMap({'en-US': 'defined'}))
        }
        return verbs

    @staticmethod
    def define_activities():
        activities = {
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
        return activities

