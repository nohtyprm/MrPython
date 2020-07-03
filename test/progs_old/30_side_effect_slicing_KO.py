##!FAIL: SideEffectWarning[append]@8:4
def f(P):
    """list[list[int]] -> int"""
    
    #K: list[list[int]]
    K = P[:]
    
    K[0].append(1)
    
    return 0