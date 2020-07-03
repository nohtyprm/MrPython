##!FAIL: WrongFunctionDefError[f]@3:0

def f(x, y):
    return 2 * (x + y)

assert f(1, 2) == 6
