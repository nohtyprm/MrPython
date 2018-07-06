
AVAILABLE_LOCALE_KEYS = { 'fr', 'en' }

TRANSLATOR_LOCALE_KEY = None

def set_translator_locale(locale_key):
    global TRANSLATOR_LOCALE_KEY
    if locale_key not in AVAILABLE_LOCALE_KEYS:
        print("Warning: locale key '{}' not available, will use default")
        locale_key = 'fr'

    TRANSLATOR_LOCALE_KEY = locale_key


TRANSLATOR_DICT = {
    "Import problem" : { 'fr' : "Problème d'import"}
    , "the module '{}' is not supported in Python101" : { 'fr' : "le module '{}' n'est pas disponible en Python101"}
    , "Signature problem" : { 'fr' : "Problème de signature"}
    , "I don't understand the signature of function '{}'" : { 'fr' : "je ne comprends pas la signature de la fonction '{}'"}
    , "Function arity issue" : { 'fr' : "Problème d'arité" }
    , "the signature of function '{}' defines {} parameters, but there are {} effectively: {}"
    : { 'fr' : "la signature de la fonction '{}' definit {} paramètre(s), mais il y en a {} effectivement : {}"}
    , 'Not-Python101' : { 'fr' : "Non-Python101"}
    , "this construction is not available in Python101 (try expert mode for standard Python)"
    : { 'fr' : "cette construction n'est pas disponible en Python101 (vous pouvez essayer le mode expert pour faire du Python standard)"}
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

