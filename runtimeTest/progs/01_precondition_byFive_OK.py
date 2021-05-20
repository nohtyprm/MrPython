def byFive(x : int) -> float:
    """
       Precondition : (x % 5 == 0)
    """
    return x / 5

x : int
x = 50

assert byFive(x) == 10