##!FAIL: Erreur: ligne 5

def fact(n : int) -> int:
    """Retourne la factorielle de n.
       Precondition : n >= 0
    """

    acc : int # accumulateur
    acc = 1

    i : int # compteur
    i = 2

    while i <= n:
        acc = acc * i
        i = i + 1

    return acc

# Jeu de tests
assert fact(-1) == fact(1) == 1
assert fact(1) == 1
assert fact(2) == 2
assert fact(3) == 6
assert fact(4) == 24
assert fact(5) == 120
assert fact(6) == 720

