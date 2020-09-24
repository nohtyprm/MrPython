##!FAIL: SlicingError[dict[K:V]]@7:9

def dict_ajout(dico : Dict[K, V], k : K, v : V) -> Dict[K, V]:
    """"""

    rd : Dict[K, V]
    rd = dico[:]

    rd[k] = v
    return rd
