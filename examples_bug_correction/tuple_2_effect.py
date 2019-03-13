def bad_function(T):
    '''tuple[int,int] -> int'''

    #a : tuple[tuple[tuple[int,int],int],int]
    a = (((2,3),1),4)
    # y : int
    # d : tuple[int,int]
    # c : int
    ((d,y),c) = a
    #b: int
    b = 3
    #__type_check(d)
    return 0

assert bad_function((1,2)) == 0
assert bad_function((3,2)) == 0
