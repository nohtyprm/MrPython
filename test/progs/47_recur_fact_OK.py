
def fact(n : int) -> int:
    """precondition: n >= 0
    """
    if n == 0:
        return 1
    else:
        return n * fact(n - 1)


def fib(n : int) -> int:
    """precondition: n >= 0
    """
    if n == 0:
        return 1
    elif n == 1:
        return 1
    else:
        return fib(n-2) + fib(n-1)


def iseven(n : int) -> bool:
    """precondition: n >= 0
    """
    if n == 0:
        return True
    else:
        return isodd(n-1)

def isodd(n : int) -> bool:
    """precondition: n >= 0
    """
    if n == 0:
        return False
    elif n == 1:
        return True
    else:
        return iseven(n-1)
