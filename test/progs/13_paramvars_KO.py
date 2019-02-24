##!FAIL: ParameterInAssignmentError[x]@7:4

def f(x):
    """ int -> int """

    # x : int
    x = 42

    return 42

assert f(12) == 42
assert f(32) == 42

