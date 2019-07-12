##!FAIL: SideEffectWarning[append]@16:4
def f(P):
    """list[int] -> int"""
    #T:tuple[list[list[int]], list[list[int]]]
    T = ([[]], [[]])
    #M: list[list[int]]
    #N: list[list[int]]
    M,N = T
    
    #K: list[list[int]]
    #L: list[list[int]]
    K, L = T
    K.append(P)
    
    #side effect
    M[0].append(4)
    return 0
