##!FAIL: HeterogenousElementError[str]@23:20

def renverse(l : List[T]) -> List[T]:
    """Renverse la liste (l'itérable) l.
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
assert renverse([1, 2, 3, 4, 5]) == [5, 4, 3, 2, 1]
assert renverse([]) == []
assert renverse([1, "two", 3, 4, 5]) == [5, 4, 3, "two", 1]
