def bad_function(T):
    '''tuple[int,int] -> int'''

    #a : tuple[tuple[int,int],int]
    a = ((1,2),4)
    #d : tuple[int,int]
    #g: int
    (d,g) = a
    return 0

assert bad_function((1,2)) == 0
assert bad_function((3,2)) == 0