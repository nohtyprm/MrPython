##!FAIL:TypeComparisonError[tuple[Number,Number]/tuple[int,int,int]]@21:26

import math # pour math.sqrt

def distance(p1, p2):
    """tuple[Number, Number] * tuple[Number, Number] -> float
    
    retourne la distance entre les points p1 et p2."""
    
    # x1 : Number (abscisse de P1)
    # y1 : Number (ordonnée de P1)
    x1, y1 = p1
    
    # x2 : Number (abscisse de P2)
    # y2 : Number (ordonnée de P2)
    x2, y2 = p2
    
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Jeu de tests
assert distance( (0, 0), (1, 1, 1) ) == math.sqrt(2)
assert distance( (2, 2), (2, 2) ) == 0.0

