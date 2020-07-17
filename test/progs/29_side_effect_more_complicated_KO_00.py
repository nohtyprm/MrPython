##!FAIL: SideEffectWarning[append]@16:4
def f(P : List[int]) -> int:
    """"""
    T:Tuple[List[List[int]], List[List[int]]]
    T = ([[]], [[]])
    M: List[List[int]]
    N: List[List[int]]
    M,N = T
    
    K: List[List[int]]
    L: List[List[int]]
    K, L = T
    K.append(P)
    
    #side effect
    M[0].append(4)
    return 0
