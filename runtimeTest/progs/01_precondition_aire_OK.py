import math

def aire_triangle(a : float, b : float, c : float) -> float:
    """
    PrEcOnDiTiOn : (a>0) and (b>0) and (c>0)
    """

    p : float
    p = (a + b + c) / 2

    return math.sqrt(p * (p - a) * (p - b) * (p - c))

# Jeu de tests
assert aire_triangle(3, 4, 5) == 6.0
assert aire_triangle(13, 14, 15) == 84.0
assert aire_triangle(1, 1, 1) == math.sqrt(3 / 16)