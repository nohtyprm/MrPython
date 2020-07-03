##!FAIL: TypeComparisonError[list[_]/str]@23:16

def renverse(L):
    """ list[alpha] -> list[alpha]
    renverse la liste (l'itérable) L.
    """

    # LR : list[alpha]  (liste résultat)
    LR = []

    # i : int (position)
    i = len(L) - 1

    while i >= 0:
        LR.append(L[i])
        i = i - 1

    return LR

# Jeu de tests
assert renverse([1, 2, 3, 4, 5]) == [5, 4, 3, 2, 1]
assert renverse([]) == []
assert renverse("toto") == ["o", "t", "o", "t"]
