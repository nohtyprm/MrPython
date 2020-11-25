##!FAIL: ReservedFunctionNameError[add]@3:0

def add(x : int) -> int:
    return x + 1

assert add(42) == 43
