
AVAILABLE_LOCALE_KEYS = { 'fr', 'en' }

TRANSLATOR_LOCALE_KEY = None

def set_translator_locale(locale_key):
    global TRANSLATOR_LOCALE_KEY
    if locale_key not in AVAILABLE_LOCALE_KEYS:
        print("Warning: locale key '{}' not available, will use default")
        locale_key = None
    elif locale_key == "en":
        locale_key = None  # default

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
    ,"Type error" : { 'fr' : "Erreur de typage" }
    ,"Name error (unitialized variable?)" : { 'fr': "Erreur de nommage (variable non initialisée ?)" }
    ,"Division by zero" : { 'fr' : "Division par zéro" }
    ,"Assertion error (failed test?)" : { 'fr' : "Erreur d'assertion (test invalide ?)" }
    # status
    ,"Saving file" : { 'fr' : "Enregistre" }
}

def tr(msg):
    '''
    Translates a string in french according to the translator_dict
    '''
    global TRANSLATOR_LOCALE_KEY

    #print("tr msg=" + msg)
    #print("locale key = " + str(TRANSLATOR_LOCALE_KEY))

    if TRANSLATOR_LOCALE_KEY is None:
        return msg

    vals = TRANSLATOR_DICT.get(msg, None)

    if vals is None:
        return msg

    tmsg = vals.get(TRANSLATOR_LOCALE_KEY, None)
    if tmsg is None:
        return msg

    return tmsg

