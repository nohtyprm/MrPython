def longueur(l : Iterable[T]) -> int:
    """Retourne la longueur de L
       Précondition : l != []
    """

    long : int
    long = 0

    e : T
    for e in l:
        long = long + 1

    return long


assert longueur([1, 2, 3, 4]) == 4
assert longueur([1,2]) == 2


def liste_longeurs(ll : Iterable[Iterable[T]]) -> List[int]:
    """Retourne la liste des longueurs de listes de L
       Précondition : len(ll) != 0
    """

    lr : List[int]
    lr = []

    l : Iterable[T]
    for l in ll:
        lr.append(longueur(l))

    return lr

assert liste_longeurs([[3], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4]]) == [1, 1, 2, 3, 4]
assert liste_longeurs([[longueur([1])], [longueur([1])], [longueur([1, 2])]
                    , [longueur([1, 2, 3])]
                    , [longueur([1, 2, 3, 4])]]) == [1, 1, 1, 1, 1]

