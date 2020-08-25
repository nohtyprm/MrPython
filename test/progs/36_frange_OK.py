def f() -> int:
    """ """

    r : range
    r = range(1, 11)

    i : int
    for i in r:
        print(i)

    return r[4]

assert f() == 5

def g(r : range) -> int:
    """ """

    s : int
    s = 0

    i : int
    for i in r:
        s = s + i

    return s

assert g(range(1, 10)) == 45
