
def dict_ajout(dico : Dict[K, V], k : K, v : V) -> Dict[K, V]:
    """"""

    rd : Dict[K, V]
    rd = {kk: vv for (kk, vv) in dico.items()}

    rd[k] = v
    return rd

assert dict_ajout({'a' : 1, 'b' : 2}, 'c', 3) == {'a' : 1, 'b' : 2, 'c' : 3}
assert dict_ajout({'a' : 1, 'b' : 2, 'c' : 4}, 'c', 3) == {'a' : 1, 'b' : 2, 'c' : 3}
