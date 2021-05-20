##!FAIL: Erreur: ligne 5

def byFive(x : int) -> float:
    """
       Precondition : (x % 5 == 0)
    """
    return x / 5

x : int
x = 42

assert byFive(x) == 8.4