
def prec_div(x : float,y : float) -> float:
    """
       Precondition : y < 0
    """

    if y > 0:
        return x / y
   

# Jeu de tests
assert prec_div(3 / 3) == 1
assert prec_div(9 / 3) == 3
assert prec_div(0 / 3) == 0

