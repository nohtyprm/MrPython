
def valeur_absolue(x : float) -> float:
    """Retourne la valeur absolue de x.
    """

    if x >= 0:
        return x
    else:
        return -x

# Jeu de tests
assert valeur_absolue(3) == 3
assert valeur_absolue(-3) == 3
assert valeur_absolue(1.5 - 2.5) == valeur_absolue(2.5 - 1.5)
assert valeur_absolue(0) == 0
assert valeur_absolue(-0) == 0
