def moyenne_trois_nb(a, b, c):
    """
    Number * Number * Number -> float
    
    retourne la moyenne arithmétique des trois nombres a, b et c.
    """
    
    return (a + b + c) / 3.0   # remarque : division flottante

# Jeu de tests
assert moyenne_trois_nb(3, 6, -3) == 2.0
assert moyenne_trois_nb(3, 0, -3) == 0.0
assert moyenne_trois_nb(1.5, 2.5, 1.0) == 5.0 / 3.0
assert moyenne_trois_nb(3, 6, 3) == 4.0
assert moyenne_trois_nb(1, 2, 3) == 2.0
assert moyenne_trois_nb(1, 1, 1) == 1.0
assert moyenne_trois_nb(3, 6, 3) == 4.0
assert moyenne_trois_nb(1, 2, 3) == 2.0

