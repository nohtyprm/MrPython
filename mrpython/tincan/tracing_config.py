"""
Contains and modify MrPython behaviour, filepaths for input/output, LRS properties,
xAPI verbs and activities, error categories and function_names
"""
from tincan import (
    Verb,
    Activity,
    LanguageMap,
    ActivityDefinition,
)
from configHandler import MrPythonConf
import os

# MrPython behaviour and filepaths

tracing_active = True  # Create the statements
send_to_LRS = False and tracing_active  # Send the created statements to the LRS
debug_log = True and tracing_active  # Keep a record of all statements produced in debug_filepath
backup_filepath =  os.path.join(MrPythonConf.GetUserCfgDir(), 'tracing_backup.json')
debug_filepath = os.path.join(MrPythonConf.GetUserCfgDir(), 'tracing_debug.txt')
session_filepath = os.path.join(MrPythonConf.GetUserCfgDir(), 'tracing_session.txt')

# LRS properties

lrs_endpoint = "https://lrsmocah.lip6.fr/data/xAPI"
lrs_version = "1.0.1" # 1.0.1 | 1.0.0 | 0.95 | 0.9
lrs_username = "8cba24cdc8d3306dd8cd917d586fb5972789efbc"
lrs_password = "3c480cc7dac4b8556120a9f37467371f495d8210"

# xAPI verbs and activites

verbs = {
    "opened": Verb(
        id="http://activitystrea.ms/schema/1.0/open", display=LanguageMap({'en-US': 'opened'})),
    "closed": Verb(
        id="http://activitystrea.ms/schema/1.0/close", display=LanguageMap({'en-US': 'closed'})),
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
    "typed": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/typed", display=LanguageMap({'en-US': 'typed'})),
    "modified": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/modified", display=LanguageMap({'en-US': 'modified'})),
    "deleted": Verb(
        id="http://activitystrea.ms/schema/1.0/delete", display=LanguageMap({'en-US': 'deleted'})),
    "inserted": Verb(
        id="http://activitystrea.ms/schema/1.0/insert", display=LanguageMap({'en-US': 'inserted'})),
    "copied": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/copied", display=LanguageMap({'en-US': 'copied'})),
    "undid": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/undid", display=LanguageMap({'en-US': 'undid'})),
    "redid": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/redid", display=LanguageMap({'en-US': 'redid'})),
    "initialized": Verb(
        id="http://activitystrea.ms/schema/1.0/initialized", display=LanguageMap({'en-US': 'initialized'})),
    "updated": Verb(
        id="http://activitystrea.ms/schema/1.0/update", display=LanguageMap({'en-US': 'updated'})),
    "entered": Verb(
        id="https://www.lip6.fr/mocah/invalidURI/verbs/entered", display=LanguageMap({'en-US': 'entered'})),
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
    "output-console": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/output-console",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'the output console of MrPython'}))),
    "execution": Activity(
            id="https://www.lip6.fr/mocah/invalidURI/activity-types/execution",
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': 'a programming execution'}),
                description=LanguageMap({'en-US': 'execution of the student\'s editor'}))),
    "evaluation": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation",
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
    "keyword": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/keyword",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a keyword'}))),
    "instruction": Activity(
        id="https://www.lip6.fr/mocah/invalidURI/activity-types/instruction",
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': 'a programming instruction'}))),
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

# Errors and functions details. Mapping error class_name -> error category

error_groups = {"AssertionInFunctionWarning": "Semantique&Python101",
                 "ForbiddenMultiAssign": "Syntaxe&Python101",
                 "ContainerAssignTypeError": "Semantique&Python101",
                 "ContainerAssignEmptyError": "Autre",
                 "UnhashableKeyError": "Typage",
                 "IndexingSequenceNotNumeric": "Typage",
                 "IndexingDictKeyTypeError": "Typage",
                 "IndexingError": "Typage",
                 "IteratorTypeError": "Typage",
                 "MembershipTypeError": "Semantique&Python101",
                 "UnhashableElementError": "Typage",
                 "SlicingError": "Typage",
                 "VariableTypeError": "Typage",
                 "ParameterInAssignmentError": "Semantique&Python101",
                 "IterVariableInEnvError": "Semantique&Python101",
                 "ParameterInForError": "Semantique&Python101",
                 "DeadVariableDefineError": "Semantique&Python101",
                 "ParameterInCompError": "Semantique&Python101",
                 "DeadVariableUseError": "Semantique&Python101",
                 "WithVariableInEnvError": "Semantique&Python101",
                 "ParameterInWithError": "Semantique&Python101",
                 "CallArityError": "Semantique",
                 "UnknownFunctionError": "Syntaxe",
                 "CallArgumentError": "Semantique",
                 "SideEffectWarning": "Semantique&Python101",
                 "CompareConditionError": "Typage&Python101",
                 "CompareConditionWarning": "Typage",
                 "DeclarationError": "Typage&Python101",
                 "DuplicateMultiAssignError": "Typage",
                 "EmptyTupleError": "Semantique&Python101",
                 "CallNotNoneWarning": "Semantique",
                 "ExprAsInstrWarning": "Semantique",
                 "FunctionArityError": "Semantique",
                 "HeterogeneousElementError": "Typage&Python101",
                 "OptionCoercionWarning": "Typage&Python101",
                 "TypeImprecisionWarning": "Typage&Python101",
                 "TypeComparisonError": "Typage",
                 "TypeExpectationError": "Typage",
                 "TupleTypeExpectationError": "Typage",
                 "NoTestError": "Tests&Python101",
                 "OneTestWarning": "Tests&Python101",
                 "UnsupportedNumericTypeError": "Syntaxe&Python101",
                 "ERangeArgumentError": "Semantique",
                 "NoReturnInFunctionError": "Semantique",
                 "SignatureTrailingError": "Syntaxe&Python101",
                 "SignatureParseError": "Syntaxe",
                 "TupleDestructArityError": "Semantique",
                 "FunctionUnhashableError": "Typage&Python101",
                 "DuplicateTypeDefError": "Typage&Python101",
                 "TypeDefParseError": "Syntaxe&Python101",
                 "UnknownTypeAliasError": "Typage&Python101",
                 "UnknownVariableError": "Semantique",
                 "WrongReturnTypeError": "Typage",
                 "UnsupportedImportError": "Autre&Python101",
                 "MissingTestsWarning": "Tests&Python101",
                 "UnsupportedNodeError": "Autre&Python101",
                 "WrongFunctionDefError": "Typage&Python101",
                 "UnsupportedTopLevelNodeError": "Semantique&Python101",
                 "IndentationError": "Syntaxe",
                 "SyntaxError": "Syntaxe",
                 "Exception": "Autre",
                 "TypeError": "Typage",
                 "NameError": "Syntaxe",
                 "ZeroDivisionError": "Semantique",
                 "AssertionError": "Tests",
                 "OtherExecutionError": "Autre",
                 "UserTerminatedError": "Autre"}

# Mapping function name -> theme number, exercise number, question number
function_names_context = {
    "aire_disque": {
      "theme-number": 1,
      "exercise-number": 1,
      "question-number": 1
    },
    "excursion": {
      "theme-number": 1,
      "exercise-number": 2,
      "question-number": 1
    }
  }