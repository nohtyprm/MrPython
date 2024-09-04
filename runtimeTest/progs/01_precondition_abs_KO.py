##!FAIL: Erreur: ligne 26

def valeur_absolue(x : float) -> float:
    """
        Retourne la valeur absolue de x.
        Precondition :
                    x != 0
    """

    abs_x : float
    abs_x = 0
    
    # stockage de la valeur absolue, le choix de 0 pour
    # l'initialisation est ici arbitraire

    if x >= 0:
        abs_x = x # conséquent
    else:
        abs_x = -x # alternant
    return abs_x

# Jeu de tests
assert valeur_absolue(3) == 3
assert valeur_absolue(-3) == 3
assert valeur_absolue(1.5 - 2.5) == valeur_absolue(2.5 - 1.5)
assert valeur_absolue(0) == 0
