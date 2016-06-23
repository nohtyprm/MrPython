
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
    "New" : { 'fr': "Nouveau" },
    "New Ctrl-N" : { 'fr': "Nouveau Ctrl-N" },
    "Open" : { 'fr': "Ouvrir" }
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

