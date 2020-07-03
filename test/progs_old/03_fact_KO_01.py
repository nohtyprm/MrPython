##!FAIL: CompareConditionError[int/bool]@14:10

def fact(n):
    """ int -> int
    retourne la factorielle de n.
    """

    # acc : int (accumulateur)
    acc = 1

    # i : int (compteur)
    i = 2

    while i <= True:
        acc = acc * i
        i = i + 1

    return acc

# Jeu de tests
assert fact(0) == fact(1) == 1
assert fact(1) == 1
assert fact(2) == 2
assert fact(3) == 6
assert fact(4) == 24
assert fact(5) == 120
assert fact(6) == 720

