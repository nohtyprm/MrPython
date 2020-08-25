##!FAIL: TupleTypeExpectationError[int]@6:4


def f(x : int) -> int:
    """Destruction of a non-tuple type """
    a, b = x
    return a + b > 0
