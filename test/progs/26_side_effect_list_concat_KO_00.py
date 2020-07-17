##!FAIL: SideEffectWarning[append]@7:4

def side_effect(l : List[int]) -> int:
    """"""
    ll : List[List[int]]
    ll = [l] + [[]]
    ll[0].append(2)
    return 0
