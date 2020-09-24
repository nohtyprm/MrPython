# Exercice 1.1 : Moyenne de trois nombres

## Question 1

def moyenne_trois_nb(a : float, b : float, c : float) -> float:
    """Retourne la moyenne arithmétique des trois nombres a, b et c.
    """
    return (a + b + c) / 3.0

# Jeu de tests
assert moyenne_trois_nb(3, 6, -3) == 2.0
assert moyenne_trois_nb(3, 0, -3) == 0.0
assert moyenne_trois_nb(1.5, 2.5, 1.0) == 5.0 / 3.0
assert moyenne_trois_nb(3, 6, 3) == 4.0
assert moyenne_trois_nb(1, 2, 3) == 2.0
assert moyenne_trois_nb(1, 1, 1) == 1.0

## Question 2 : moyenne pondérée

def moyenne_ponderee(a : float, b : float, c : float,
                     pa : float, pb : float, pc : float) -> float:
    """Hypothèse : pa + pb + pc != 0
    Retourne la moyenne des trois nombres a, b, c, pondérés
    respectivement par pa (pondération pour a), pb et pc.
    """
    return ((a * pa) + (b * pb) + (c * pc)) / (pa + pb + pc)

# Jeu de tests
assert moyenne_ponderee(1, 1, 1, 3, 6, -3) == 1.0
assert moyenne_ponderee(2, 3, 4, 1, 1, 1) == 3.0
assert moyenne_ponderee(1, 0, 4, 2, 1, 2) == 2.0
