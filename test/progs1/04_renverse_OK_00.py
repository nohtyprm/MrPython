
def prec_renverse(l : Sequence[T]) -> List[T]:
    """
    Precondition : l == []
    """

    lr : List[T]  # liste résultat
    lr = []

    i : int # position
    i = len(l) - 1

    while i >= 0:
        lr.append(l[i])
        i = i - 1

    return lr

# Jeu de tests
assert prec_renverse([1, 2, 3, 4, 5]) == [5, 4, 3, 2, 1]
assert prec_renverse([]) == []
assert prec_renverse("toto") == ["o", "t", "o", "t"]
