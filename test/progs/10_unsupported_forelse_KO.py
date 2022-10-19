##!FAIL: UnsupportedElseError[For]@9:4

def f(n : int) -> int:
    """ """

    res : int = 0

    m : int
    for m in range(1, n):
        res = res + m
    else:
        res = res +1

    return res

