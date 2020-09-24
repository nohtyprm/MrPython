##!FAIL: SideEffectWarning[append]@8:4
def f(P : List[List[int]]) -> int:
    """"""
    
    K: List[List[int]]
    K = P[:]
    
    K[0].append(1)
    
    return 0
