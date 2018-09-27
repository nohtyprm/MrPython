
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
    : { 'fr' : "cette construction n'est pas disponible en Python101 (vous pouvez essayer le mode expert pour faire du Python standard)" }
    , "Declaration problem" : { 'fr' : 'Problème de déclaration'}
    , "Missing variable declaration '{}'" : { 'fr' : "Il manque la declaration de la variable '{}'" }
    , "Wrong variable name in declaration, it should be '{}'" : { 'fr' : "le nom de variable est erroné dans la déclaration, cela devrait être '{}'"}
    , "Missing ':' character before variable type declaration" : { 'fr' : "il manque le caractère ':' avant le type de la variable"}
    , "I don't understand the declared type for variable '{}'" : { 'fr' : "je ne comprends pas le type déclaré pour la variable '{}'"}
    , "Variable problem" : { 'fr' : "Problème de variable"}
    , "there is such variable of name '{}'" : { 'fr' : "il n'y a pas de variable de nom '{}'"}
    , "Call problem" : { 'fr' : "Problème d'appel de fonction"}
    , "the {}-th argument in call to function '{}' is erroneous" : { 'fr' : "le {}-ième argument dans l'appel à '{}' est erroné"}
    , "Number problem" : { 'fr' : "Problème numérique"}
    , "this numeric value is not supported in Python 101: {} ({})" : { 'fr' : "cette valeur numérique n'est pas disponible en Python101 : {} ({})"}
    , "Call problem" : { 'fr' : "Problème d'appel"}
    , "I don't know any function named '{}'" : { 'fr' : "je ne connais pas de fonction dont le nom est '{}'"}
    , "Incompatible types" : { 'fr' : "Types incompatibles"}
    , "Expecting type '{}' but instead found: {}" : { 'fr' : "j'attendais le type '{}' mais cette expression est plutôt de type: {}"}
    , "Comparison error" : { 'fr' : "Erreur de comparaison"}
    , "The two operands of the comparision should have the same type" : { 'fr' : "Les deux opérandes de la comparaison devraient être du même type"}
    , "Bad variable" : { 'fr' : "Mauvaise utilisation de variable"}
    , "Forbidden use of a variable that is not in scope (Python101 scoping rule)" : { 'fr' : "Il n'est pas autorisé en Python101 d'utiliser cette variable dont la portée est erronée" }
    , "Bad indexing" : { 'fr' : "Problème d'indexation" }
    , "One can only index a sequence or a dictionnary, not a '{}'" : { 'fr' : "On ne peut indexer qu'une séquence ou un dictionnaire, pas un '{}'" }
    , "Bad index" : { 'fr' : "Erreur d'index"}
    , "Sequence index must be an integer" : { 'fr' : "L'index de sequence doit être un entier"}
    , "Heterogeneous elements (Python101 restriction)" : { 'fr' : "Eléments hétérogènes (restriction Python 101)"}
    , "All elements of must be of the same type '{}' but this element has incompatible type: {}" : { 'fr' : "Tous les élements doivent être du même type '{}' mais cet élément est d'un type incompatible: {}" }
    , "Unused variable name '{}' in declaration" : { 'fr' : "La variable '{}' déclarée n'est pas utilisée" }
    , "Tuple destruct error" : { 'fr' : "Erreur de destructuration de n'uplet" }
    , "Wrong number of variables to destruct tuple, expecting {} variables but {} given" : { 'fr' : "J'attends {} variables pour destructurer le n-uplet mais vous en spécifiez {}"}
    , "In Python101 the `asserts` are reserved for test cases, however one assert is present in the body of function '{}'" : { 'fr' : "En Python101 `assert` est réservé pour les jeux de tests, mais vous utilisez `assert` dans le corps de la fonction '{}'" }
    , "Assertion issue" : { 'fr' : "Problème d'assertion" }
    , "Wrong return type" : { 'fr' : "Type de retour erroné" }
    , "The declared return type for function '{}' is '{}' but the return expression has incompatible type: {}" : { 'fr' : "Le type de retour déclaré pour la fonction '{}' est '{}' mais l'expression du `return` est de type incompatible: {}" }
    , "Expression problem" : { 'fr' : "Problème d'expression" }
    , "This expression is in instruction position, the computed value is lost" : { 'fr' : "Cette expression est placée en position d'instruction, la valeur calculée est perdue" }
    , "Return problem" : { 'fr' : "Problème de retour" }
    , "The function '{}' should have `return` statement(s)" : { 'fr' : "Il n'y a aucun `return` dans la fonction '{}', ce n'est pas normal" }
    , 'Wrong definition' : { 'fr' : "Mauvaise définition" }
    , "The function '{}' has no correct specification." : { 'fr' : "La fonction '{}' n'est pas spécifée correctement." }
    , 'Wrong statement' : { 'fr' : "Instruction non-supportée" }
    , "In Python 101 this statement cannot be done outside a function body (try expert mode for standard Python)"
    : { 'fr' : "En Python101 cette d'instruction ne peut apparaître en dehors du corps d'une fonction (essayez le mode expert pour faire du Python standard)" }
    , "calling '{}' with {} argument(s) but expecting: {}" : { 'fr' : "La fonction '{}' est appelée avec {} argument(s) mais elle en attend : {}" }
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

