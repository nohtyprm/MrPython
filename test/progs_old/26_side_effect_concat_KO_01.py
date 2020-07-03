##!FAIL: SideEffectWarning[append]@4:5
def f(LL):
    """list[list[int]] -> int"""
    (LL + [])[0].append(1)
    return 0
