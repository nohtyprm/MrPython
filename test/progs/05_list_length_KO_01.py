##!FAIL: ParameterInAssignmentError[l]@6:4

def longueur(l : Iterable[T]) -> int:
    """Retourne la longueur de L"""

    l : int
    l = 0

    e : T
    for e in l:
        print(e)
        long = long + 1

    return long


assert longueur([1, 2, 3, 4]) == 4
assert longueur([]) == 0


def list_length(ll : Iterable[Iterable[T]]) -> int:
    """Retourne la liste des longueurs de listes de L"""

    lr : List[int]
    lr = []

    l : Iterable[T]
    for l in ll:
        lr.append(longueur(l))

    return lr

assert list_length([[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4]]) == [0, 1, 2, 3, 4]
assert list_length([]) == []
assert list_length([[longueur([])], [longueur([1])], [longueur([1, 2])]
                    , [longueur([1, 2, 3])]
                    , [longueur([1, 2, 3, 4])]]) == [1, 1, 1, 1, 1]

