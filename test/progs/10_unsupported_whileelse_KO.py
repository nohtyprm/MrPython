##!FAIL: UnsupportedElseError[While]@10:4

def f(n : int) -> int:
    """ """

    res : int = 0

    m : int = 1

    while m < n:
        res = res + m
        m = m + 1
    else:
        res = res +1

    return res

