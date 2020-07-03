##!FAIL: SideEffectWarning[add]@6:4
def f(P):
    """list[set[int]] -> int"""
    #K: set[int]
    K = P[0]
    K.add(1)
    return 0