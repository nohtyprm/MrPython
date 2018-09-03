
def longueur(L):
    """Iterable[α] -> int
    Retourne la longueur de L"""

    # l : int
    l = 0

    # e : α
    for e in L:
        l = l + 1

    return l


assert longueur([1, 2, 3, 4]) == 4
assert longueur([]) == 0


def list_length(LL):
    """Iterable[Iterable[α]] -> list[int]
    Retourne la liste des longueurs de listes de L"""

    # LR : list[int]
    LR = []

    # L : Iterable[α]
    for L in LL:
        LR.append(longueur(L))

    return LR

assert list_length([[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4]]) == [0, 1, 2, 3, 4]
assert list_length([]) == []
assert list_length([longueur([]), longueur([1]), longueur([1, 2])
                    , longueur([1, 2, 3])
                    , longueur([1, 2, 3, 4])]) == [1, 1, 1, 1, 1]

