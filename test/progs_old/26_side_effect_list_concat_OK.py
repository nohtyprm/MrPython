def side_effect(L):
    """list[int] ->int"""
    #M : list[int]
    M = L + []
    M.append(2)
    return 0