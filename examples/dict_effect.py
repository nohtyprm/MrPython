def bad_function(D):
    """ dict[int:int] -> int """
    
    # L : dict[int:dict[int:int]]
    L = {1:D,2:{1:2}}
    L[2] = {1:2}

    return 0

assert bad_function({1:1}) == 0
assert bad_function({3:2}) == 0
