def bad_function(T):
    '''tuple[int,int] -> int'''

    #e : tuple[tuple[int,int],int]
    e = (T,1)
    #a : int
    #b : int
    #c : int
    a,b,c = e
    return 0

assert bad_function((1,2)) == 0
assert bad_function((3,2)) == 0
