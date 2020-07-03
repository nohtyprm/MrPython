##!FAIL:UnknownVariableError[q]@16:26

import math

def aire_triangle(a,b,c):
    """ Number * Number * Number -> float
    Hypothèse : (a>0) and (b>0) and (c>0)
    Hypothèse : les côtés a, b et c définissent bien un triangle.

    retourne l'aire du triangle dont les côtés sont de 
             longueurs a, b, et c."""

    # p : float
    p = (a + b + c) / 2

    return math.sqrt(p * (q - a) * (p - b) * (p - c))

# Jeu de tests (Etape 3)
assert aire_triangle(3, 4, 5) == 6.0
assert aire_triangle(13, 14, 15) == 84.0
assert aire_triangle(1, 1, 1) == math.sqrt(3 / 16)
assert aire_triangle(2, 3, 5) == 0.0  # c'est un triangle plat...
