
AVAILABLE_LOCALE_KEYS = { 'fr', 'en' }

TRANSLATOR_LOCALE_KEY = None

def set_translator_locale(locale_key):
    global TRANSLATOR_LOCALE_KEY
    if locale_key not in AVAILABLE_LOCALE_KEYS:
        print("Warning: locale key '{}' not available, will use default")
        locale_key = 'fr'

    TRANSLATOR_LOCALE_KEY = locale_key


TRANSLATOR_DICT = {
    # toolbar
    "New Ctrl-N" : { 'fr': "Nouveau Ctrl-N" }
    ,"Open Ctrl-O" : { 'fr': "Ouvrir Ctrl-O" }
    ,"Save Ctrl-S" : { 'fr': "Sauvegarder Ctrl-S" }
    ,"Mode Ctrl-M" : { 'fr': "Mode Ctrl-M" }
    ,"Run Ctrl-R" : { 'fr': "Interpréter Ctrl-R" }
    # modeline
    ,"student" : { 'fr': "étudiant" }
    ,"full" : { 'fr': "expert" }
    # interprète
    ,"Error" : { 'fr': "Erreur" }
    ,"Warning" : { 'fr': "Attention" }
    ,"Evaluating: " : { 'fr': "Evaluation de : " }
    ,"Interpretation of: " : { 'fr' : "Interprétation de : " }
    ,"Bad indentation" : { 'fr' : "Mauvaise indentation" }
    ,"Syntax error" : { 'fr' : "Erreur de syntaxe" }
    ,"Type error" : { 'fr' : "Erreur Python" }
    ,"Name error (unitialized variable?)" : { 'fr': "Erreur de nommage (variable non initialisée ?)" }
    ,"Division by zero" : { 'fr' : "Division par zéro" }
    ,"Assertion error (failed test?)" : { 'fr' : "Erreur d'assertion (test invalide ?)" }
    ,"Precondition error" : { 'fr' : "Erreur de précondition" }
    ,"User interruption" : { 'fr' : "Interruption par l'utilisateur"}
    # Erreurs de conventions
    , ": line {}\n" : { 'fr' : ": ligne {}\n"}
    ,"Missing tests" : { 'fr' : "Tests manquants"}
    ,"Untested functions: " : { 'fr' : "Fonctions non-testées : "}
    ,"All functions tested (good)" : { 'fr' : "Toutes les fonctions sont testées (bien)"}
    , '==> the program is type-checked (very good)\n' : {'fr' : '==> le programme est bien typé (très bien)\n' }
    # status
    ,"Saving file" : { 'fr' : "Enregistre" }
    ,"All the {} tests passed with success" : { 'fr' : "Les {} tests sont passés avec succès" }
    , "Only one (successful) test found, it's probably not enough" : { 'fr' : "Je n'ai trouvé qu'un seul test, il passe mais ce n'est sans doute pas suffisant" }
    , "There is no test! you have to write tests!" : { 'fr' : "Je ne trouve pas de test, il faut tester vos fonctions !" }
    , "-----\nPython101 convention errors:\n-----\n" : { 'fr' : "-----\nErreurs de convention (Python101) :\n-----\n" }
    , "\n-----\nCompilation errors (Python interpreter):\n-----\n" : { 'fr' : "\n-----\nErreurs de compilation (Interprète Python) :\n-----\n" }
    , "\n-----\nExecution errors (Python interpreter):\n-----\n" : { 'fr' : "\n-----\nErreurs à l'exécution (Interprète Python) :\n-----\n" }
    
}

def tr(msg):
    global TRANSLATOR_LOCALE_KEY

    #print("tr msg=" + msg)
    #print("locale key = " + str(TRANSLATOR_LOCALE_KEY))

    if TRANSLATOR_LOCALE_KEY is None:
        TRANSLATOR_LOCALE_KEY = 'fr'  # Hack !

    vals = TRANSLATOR_DICT.get(msg, None)

    if vals is None:
        return msg

    tmsg = vals.get(TRANSLATOR_LOCALE_KEY, None)
    if tmsg is None:
        return msg

    return tmsg

