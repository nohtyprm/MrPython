##!FAIL: TypeComparisonError[Tuple[float,float]/Tuple[int,int,int]]@19:25

import math # pour math.sqrt

def distance(p1 : Tuple[float, float], p2 : Tuple[float, float]) -> float:
    """Retourne la distance entre les points p1 et p2."""

    x1 : float # abscisse de P1
    y1 : float # ordonnée de P1
    x1, y1  = p1

    x2 : float # abscisse de P2
    y2 : float # ordonnée de P2
    x2, y2 = p2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Jeu de tests
assert distance( (0, 0), (1, 1, 1) ) == math.sqrt(2)
assert distance( (2, 2), (2, 2) ) == 0.0
