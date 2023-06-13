
def groupes(f : Callable[[T], K], lst : List[T]) -> Dict[K, List[T]]:
    """
    """
    dico : Dict[K,List[T]] = dict()

    e : T
    for e in lst:
        k : K = f(e)
        if k in dico:
            dico[k].append(e)
        else:
            dico[k] = [e]

    return dico

# Jeu de tests
# TODO : str devrait être compatible avec  Iterable[str]
assert groupes(len, ["a", "as", "asd", "aa", "asdf", "qwer", "aa"]) \
       == {1 : ["a"], 2 : ["as", "aa", "aa"], 3 : ["asd"], 4 : ["asdf", "qwer"]}
