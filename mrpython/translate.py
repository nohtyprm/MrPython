
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
    ,"Evaluating: " : { 'fr': "Evaluation de : " }
    ,"Interpretation of: " : { 'fr' : "Interprétation de : " }
}

def tr(msg):
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

