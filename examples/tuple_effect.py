def bad_function(L):
    '''list[int] -> int'''

    #e : tuple[list[int],int]
    e = (L,1)
    a,b = e
    a.append(7)

    return 0

assert bad_function(([1,2])) == 0
assert bad_function([3,2,1]) == 0
