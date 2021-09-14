def division(x : float,y : float) -> float:
    """
       Precondition : y != 0
    """

    return x / y
   
# Jeu de tests
assert division(3, 3) == 1
assert division(9, 3) == 3
assert division(1, 1) == 1