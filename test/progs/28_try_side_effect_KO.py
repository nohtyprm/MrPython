##!FAIL: SideEffectWarning[append]@9:4
def f(LL : List[List[int]]) -> int:
    """"""
    M: List[int]
    M = []
    N:List[List[int]]
    N = [[], M, [1, 2]]
    M = LL[0]
    N[1].append(1)
    return 0
