##!FAIL: TypeExprParseError[Paramètre 'dico' : Je ne comprends pas le type dictionnaire déclaré : il manque le type des clés et/ou des valeurs]@3:0

def dict_ajout(dico : Dict[int], k : K, v : V) -> Dict[K, V]:
    """"""

    rd : Dict[K, V]
    rd = dico[:]

    rd[k] = v
    return rd
