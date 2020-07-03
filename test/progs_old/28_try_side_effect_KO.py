##!FAIL: SideEffectWarning[append]@9:4
def f(LL):
    """list[list[int]] -> int"""
    #M: list[int]
    M = []
    #N:list[list[int]]
    N = [[], M, [1, 2]]
    M = LL[0]
    N[1].append(1)
    return 0
