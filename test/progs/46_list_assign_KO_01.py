##!FAIL: SideEffectContainerWarning[assign]@8:8

def incrementer(l : List[int]) -> None:
    """Incrémente tous les éléments de la liste l.
    """
    i : int
    for i in range(len(l)):
        l[i] = l[i] + 1

# Jeu de tests

MaListe : List[int] = [1, 2, 3, 4, 5, 6]

assert incrementer(MaListe) == None
assert MaListe == [2, 3, 4, 5, 6, 7]


