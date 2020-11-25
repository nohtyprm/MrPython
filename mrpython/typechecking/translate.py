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
    , "Warning you've initialzed in 2 differents ways the variable: '{}'" : {'fr' : "Vous avez initailisé de 2 façons différentes la variable : '{}'"}
    , "Warning you've initialzed and not used the variable: '{}'" : {'fr' : "Attention, vous initialisez sans utiliser la variable : '{}'" }
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
    , "Missing variable declaration" : { 'fr' : "La déclaration de variable est manquante." }
    , "Wrong variable name in declaration, it should be '{}'" : { 'fr' : "le nom de variable est erroné dans la déclaration, cela devrait être '{}'"}
    , "Missing ':' character before variable type declaration" : { 'fr' : "je ne comprends pas le type déclaré pour cette variable, il manque le caractère ':'"}
    , "I don't understand the declared type for variable '{}'" : { 'fr' : "je ne comprends pas le type déclaré pour la variable '{}'"}
    , "Variable problem" : { 'fr' : "Problème de variable"}
    , "there is such variable of name '{}'" : { 'fr' : "il n'y a pas de variable de nom '{}'"}
    , "Call problem" : { 'fr' : "Problème d'appel de fonction"}
    , "the {}-th argument in call to function '{}' is erroneous" : { 'fr' : "le {}-ième argument dans l'appel à '{}' est erroné"}
    , "Number problem" : { 'fr' : "Problème numérique"}
    , "this numeric value is not supported in Python 101: {} ({})" : { 'fr' : "cette valeur numérique n'est pas disponible en Python101 : {} ({})"}
    , "Bad argument" : { 'fr' : "Mauvais argument"}
    , "This argument is not numeric." : { 'fr' : "Cet argument n'est pas numérique."}
    , "Call problem" : { 'fr' : "Problème d'appel"}
    , "I don't know any function named '{}'" : { 'fr' : "je ne connais pas de fonction dont le nom est '{}'"}
    , "Incompatible types" : { 'fr' : "Types incompatibles"}
    , "Expecting type '{}' but instead found: {}" : { 'fr' : "j'attendais le type '{}' mais cette expression est plutôt de type: {}"}
    , "Incorrect type" : { 'fr' : "Type incorrect" }
    , "Found type '{}' which is incorrect: {}" : { 'fr' : "Je trouve le type '{}' qui n'est pas correct : {}" }
    , "Comparison error" : { 'fr' : "Erreur de comparaison"}
    , "The two operands of the comparision should have the same type: '{}' vs. '{}'" : { 'fr' : "Les deux opérandes de la comparaison devraient être du même type: '{}' vs. '{}'"}
    , "Comparison issue" : { 'fr' : "Problème de comparaison"}
    , "The two operands of the comparison are only \"weakly\" compatibles: '{}' vs. '{}'" : { 'fr' : "Les types des deux opérandes de la comparaison ne sont qu'\"approximativement\" compatibles : '{}' vs. '{}'"}

    , "Bad variable" : { 'fr' : "Problème de variable"}
    , "Bad indexing" : { 'fr' : "Problème d'indexation" }
    , "One can only index a sequence or a dictionnary, not a '{}'" : { 'fr' : "On ne peut indexer qu'une séquence ou un dictionnaire, pas un '{}'" }
    , "Bad index" : { 'fr' : "Erreur d'index"}
    , "Sequence index must be an integer" : { 'fr' : "L'index de sequence doit être un entier"}
    , "Heterogeneous elements (Python101 restriction)" : { 'fr' : "Eléments hétérogènes (restriction Python 101)"}
    , "Bad slicing" : { 'fr' : "Erreur de découpage"}
    , "One can only slice a sequence (str, list), not a '{}'" : { 'fr' : "Le découpage n'est possible que sur les séquences (str, list) et non pour le type : {}" }

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
    , "The function '{}' has no documentation." : { 'fr' : "La fonction '{}' n'a pas de documentation."}
    , 'Wrong statement' : { 'fr' : "Instruction non-supportée" }
    , "In Python 101 this statement cannot be done outside a function body (try expert mode for standard Python)"
    : { 'fr' : "En Python101 cette d'instruction ne peut apparaître en dehors du corps d'une fonction (essayez le mode expert pour faire du Python standard)" }
    , "calling '{}' with {} argument(s) but expecting: {}" : { 'fr' : "La fonction '{}' est appelée avec {} argument(s) mais elle en attend : {}" }
    , "The signature of function '{}' contains some characters at the end that I do not understand: {}"
    : { 'fr' : "La signature de la fonction '{}' contient des caractères que je ne comprends pas à la fin: {}" }
    , "Assignment problem" : { 'fr' : "Problème d'affectation" }
    , "This assignment to variable '{}' is forbidden in Python101." : { 'fr' : "Cette affectation de la variable '{}' n'est pas permise en Python101 (uniquement disponible en mode expert)." }
    , "Expecting type '{}' but found '{}': there is a risk of imprecision (but it's maybe not a bug)" : { 'fr' : "J'attends le type '{}' mais j'ai trouvé '{}': il y a un risque d'imprécision (mais ce n'est peut-être pas une erreur)" }
    , "Imprecise typing" : { 'fr' : "Typage imprécis" }
    , "Expression in instruction position" : { 'fr' : "Expression en position instruction" }
    , "The value calculated of type `{}` is lost" : { 'fr' : "La valeur calcluée de type `{}` est perdue" }
    , "Forbidden use of parameter '{}' in assignment" : { 'fr' : "Le paramètre de nom `{}` ne peut être utilisé dans une affectation (ou initialisation)" }
    , "Forbidden use of parameter '{}' in with construct" : { 'fr' : "Le paramètre de nom `{}` ne peut être utilisé comme variable de la construction with" }
    , "the arguments of `range` are incorrect." : { 'fr' : 'les arguments de `range` sont incorrects.'  }
    , "The iterator variable '{}' is already in use." : { 'fr' : "La variable d'itération '{}' est déjà utilisée." }
    , "The `with` variable '{}' is already declared" : { 'fr' : "La variable '{}' du `with` est déjà déclarée" }
    , "Forbidden use of parameter '{}' as iteration variable" : { 'fr' : "Le paramètre de nom `{}` ne peut être utilisé comme variable d'itération" }
    , "Forbidden use of parameter '{}' as comprehension variable" : { 'fr' : "Le paramètre de nom `{}` ne peut être utilisé comme variable de compréhension" }
    , "Forbidden use of a \"dead\" variable name '{}' (Python101 rule)" : { 'fr' : "Il n'est pas autorisé en Python101 d'utiliser cette variable car le nom '{}' est déjà utilisé dans la fonction." }
    , "Forbidden use of variable '{}' that is not in scope (Python101 scoping rule)" : { 'fr' : "La variable '{}' ne peut-être utilisée ici (règle de portée de Python101)." }
    , "Type name error" : { 'fr' : "Erreur de type nommé" }
    , "I don't find any definition for the type: {}" : { 'fr' : "Je ne trouve pas de définition pour le type: {}" }
    , "Bad iterator" : { 'fr' : "Problème d'itération" }
    , "Expecting an iterator of tuples" : { 'fr' : "J'attends un itérable de n-uplets" }
    , "Not an iterable type: {}" : { 'fr' : "Type non itérable: {}" }
    , "Expecting precise type '{}' but found less precise type: {}" : { 'fr' : "J'attends le type précis '{}' mais le type de cette expression est moins précis: {}" }
    , "Unhashable (mutable) element forbidden in set, element type is: {}" : { 'fr' : "Un ensemble ne peut contenir de valeur mutable (non-hashable), ici l'élément est de type: {}" }
    , "Unhashable (mutable) key in dictionary, key type is: {}" : { 'fr' : "Une clé de dictionnaire ne peut être mutable (non-hashable), ici la clé est de type: {}" }
    , "Bad set" : { 'fr' : "Problème d'ensemble" }
    , "Bad dictionary" : { 'fr' : "Problème de dictionnaire" }
    , "Type declaration error" : { 'fr' : "Problème de déclaration de type" }
    , "Wrong use in signature of function '{}' of mutable (not hashable) type: {}" : { 'fr' : "Dans la signature de la fonction '{}' un type mutable (non-hashable) est utilisé de façon erronée dans la construction du type: {}" }
    , "Expecting a set" : { 'fr' : "J'attends un ensemble" }
    , "Expecting a tuple" : { 'fr' : "J'attends un n-uplet (tuple)" }
    , "Expecting an expression of tuple type, instead found type: '{}'" : { 'fr' : "J'attends une expression de type n-uplet (tuple), mais j'obtiens à la place le type: '{}'" }
    , "Type definition problem" : { 'fr' : "Problème de définition de type" }
    , "I don't understand the definition of type '{}'" : { 'fr' : "Je ne comprends pas la définition du type '{}'"}
    , "There is already a definition for type '{}'" : { 'fr' : "Il y a déjà une définition pour le type '{}'" }
    , "Variable(s) not declared: {}" : { 'fr' : "Variable(s) non-déclarée(s) : {}" }
    , "Expecting a dictionary" : { 'fr' : "J'attends un dictionnaire" }
    , "Expecting an empty dictionary" : { 'fr' : "J'attends un dictionnaire vide" }
    , "Dictionnary key must be of type: {}" : { 'fr' : "La clé de dictionnaire doit être de type: {}" }
    , "Bad membership" : { 'fr':  "Problème d'appartenance" }
    , "Membership only supported for sets and dicts, not for type: {}" : { 'fr' : "Le test d'appartenance est uniquement disponible (en Python101) pour les ensembles et les dictionnaires, et non pour le type: {}" }
    , "Bad assignment" : { 'fr' : "Problème d'affectation" }
    , "In Python101 this kind of assignment is only available for dictionaries, not for objects of type: {}" : { 'fr' : "En Python101 ce type d'affectation n'est disponible que pour les dictionnaires, le type suivant n'est pas supporté : {}" }
    , "Assignment in an empty dictionary" : { 'fr' : "Affectation dans un dictionnaire vide" }
    , "Bad variable type" : { 'fr' : "Problème de typage de variable"}
    , "Type mismatch for variable '{}', expecting '{}' instead of: {}" : { 'fr' : "La variable '{}' est déclarée avec le type '{}' qui n'est pas compatible avec le type requis: {}"}
    , "Call to '{}' may cause side effect" : {'fr' : "L'appel à la méthode '{}' risque d'avoir un effet de bord incontrôlé"}
    , "There is a risk of side effect as on the following parameter(s) {}" : {'fr' : "Il est possible qu'il y ait un effet de bord sur le(s) paramètre(s) suivant(s): {}"}
    , "Variable '{}' was declared multiple times" : { 'fr' : "La variable '{}' a été déclarée plusieurs fois"}
    , "Not a variable type declaration : it is a type alias." : { 'fr' : "ce n'est pas une déclaration de variable mais une déclaration d'alias de type."}
    , "Empty tuple" : { 'fr' : "N-uplet vide"}
    , "Python 101 does not allow empty tuples, only in expert mode" : { 'fr' : "les n-uplets vides (0-uplets ?) ne sont pas autorisés en Python101."}
    , "Missing return type" : { 'fr' : "Type de retour manquant" }
    , "I don't find the return type for function: {}" : { 'fr' : "Je ne trouve pas de type de retour pour la fonction : {}" }
    , "Missing variable declaration for variable: {}" : { 'fr' : "Il manque la déclaration de la variable: {}" }
    , "Unused variable" : { 'fr' : "Variable inutilisée" }
    , "The variable '{}' is declared but not used" : { 'fr' : "La variable '{}' est déclarée mais n'est pas utilisée."}
    , "Does not understand the declared type." : { 'fr' : "Je ne comprends pas le type déclaré." }
    , "Does not understand the declared container type." : { 'fr' : "Je ne comprends pas le type de conteneur déclaré." }
    , "Parameter '{}': {}" : { 'fr' : "Paramètre '{}' : {}"}
    , "Return type: {}" : { 'fr' : "Type de retour : {}"}
    , "Type expression problem" : { 'fr' : "Problème d'expression de type"}
    , "the `{}` type is deprecated, use `{}` instead" : { 'fr' : "le type `{}` n'est plus disponible, utiliser `{}` en remplacement" }
    , "Unsupported container type: {}" : { 'fr' : "Ce type de contenant n'est pas supporté : {}" }
    , "Does not understand the declared tuple type (missing element types)." : { 'fr' : "Je ne comprends pas le type n-uplet déclaré, il manque les types des éléments."}
    , "A dictionnary type must have two arguments: the key type and the value type" : { 'fr' : "Un type dictionnaire doit avoir exactement deux arguments: le type des clés et le type des valeurs" }
    , "Does not understand the declared dictionary type (missing key/value types)." : { 'fr' : "Je ne comprends pas le type dictionnaire déclaré : il manque le type des clés et/ou des valeurs" }
    , "The colon ':' separator is not allower in dictionnary types, use ',' instead" : { 'fr' : "le séparateur ':' n'est pas autorisé dans les types dictionnaire, utiliser plutôt la virgule ','" }
    , "Missing key,value types in dictionnary type" : { 'fr' : "Type dictionnaire incorrect : il manque le type des clés et des valeurs."}
    , "Wrong function name" : { 'fr' : "Nom de fonction incorrect"}
    , "The function name '{}' is reserved in student mode" : { 'fr' : "Le nom de fonction '{}' n'est pas autorisé en mode étudiant."}

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
