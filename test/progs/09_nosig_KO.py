##!FAIL: NoFunctionDocWarning[f]@3:0

def f(x : int, y : int) -> int:
    return 2 * (x + y)

assert f(1, 2) == 6
