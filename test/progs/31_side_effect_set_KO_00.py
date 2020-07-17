##!FAIL: SideEffectWarning[add]@6:4
def f(P : List[Set[int]]) -> int:
    """"""
    K: Set[int]
    K = P[0]
    K.add(1)
    return 0
