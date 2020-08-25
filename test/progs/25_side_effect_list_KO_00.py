##!FAIL: SideEffectWarning[append]@7:4

def side_effect(l : List[int], ll : List[List[int]]) -> int:
    """list[int] * list[list[int]]->int"""
    lll : List[List[int]]
    lll = [l, []]
    lll[0].append(2)
    return 0
