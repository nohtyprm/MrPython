def f(L, I):
    """list[int] * list[list[int]]->int"""
    #M : list[list[list[int]]]
    M = [[L, []], [[1]]]
    M[1].append([2])
    return 0

#assert f([]) == 0
#assert f([]) == 0
