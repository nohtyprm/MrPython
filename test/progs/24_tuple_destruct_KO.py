##!FAIL: TypeExpectationError[int/Expecting a tuple]@7:11


def f(x):
    """ int -> int
    Destruction of a non-tuple type """
    a, b = x
    return a + b > 0
