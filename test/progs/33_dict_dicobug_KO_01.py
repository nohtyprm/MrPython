##!FAIL: TypeExprParseError[Paramètre 'dico' : le séparateur ':' n'est pas autorisé dans les types dictionnaire, utiliser plutôt la virgule ',']@3:0

def dict_ajout(dico : Dict[K:V], k : K, v : V) -> Dict[K, V]:
    """"""

    rd : Dict[K, V]
    rd = dico[:]

    rd[k] = v
    return rd
