##!FAIL: SideEffectWarning[append]@7:4

def side_effect(L, I):
    """list[int] * list[list[int]]->int"""
    #M : list[list[int]]
    M = [L, []]
    M[0].append(2)
    return 0