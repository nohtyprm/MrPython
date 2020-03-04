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

    def test_send_statement(self):
        # construct the actor of the statement
        print("tracing_mrpython.py : sending statement")
        #print("constructing the LRS...")
        lrs = RemoteLRS(
            version=lrs_properties.version,
            endpoint=lrs_properties.endpoint,
            username=lrs_properties.username,
            password=lrs_properties.password,
        )

        # construct the actor of the statement
        #print("constructing the Actor...")
        actor = Agent(
            name='Adil0.0.0',
            mbox='mailto:tincanpython@tincanapi.com',
        )

        # construct the verb of the statement
        #print("constructing the Verb...")
        verb = Verb(
            id="https://www.lip6.fr/mocah/invalidURI/verbs/executed",
            display=LanguageMap({'en-US': 'executed'}),
        )

        # construct the object of the statement
        #print("constructing the Object...")
        object = Activity(
            id='https://www.lip6.fr/mocah/invalidURI/activity-types/program',
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'Program'}),
                description=LanguageMap({'en-US': 'a computer program'}),
                extensions={
                    "https://www.lip6.fr/mocah/invalidURI/MrPython/number-of-executions": "Nombre d'executions du fichier",
                    "https://www.lip6.fr/mocah/invalidURI/MrPython/number-of-tests": "Nombre de tests",
                    "https://www.lip6.fr/mocah/invalidURI/MrPython/programming-mode": "Mode student / Mode expert",
                    "https://www.lip6.fr/mocah/invalidURI/MrPython/filename": "Nom du fichier"
                }
            ),
        )

        result = Result(
            success=True,
            response="Succes"
        )
        # construct the actual statement
        #print("constructing the Statement...")
        statement = Statement(
            actor=actor,
            verb=verb,
            object=object,
            result=result
        )

        #print("saving the Statement...")
        response = lrs.save_statement(statement)
        if not response:
            raise ValueError("statement failed to save")


