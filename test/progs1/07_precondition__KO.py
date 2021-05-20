

def prec_f(a : float) -> float:
    """
    Précondition : (a < 0) and (a > 1)
    """

    b, (c, d, (e, _, f), _), g = (a, (2, 3, (4, 5, 6), 7), 8)

    return a + b + c + d + e + f + g


#jeu de test 
assert prec_f(1) == 1 + 1 + 2 + 3 + 4 + 6 + 8

