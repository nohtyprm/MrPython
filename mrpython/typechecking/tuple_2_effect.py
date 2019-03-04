def bad_function(T):
    '''tuple[int,int] -> int'''

    #a : tuple[tuple[tuple[int,int],int],int]
    a = (((2,3),1),4)
    # z : int
    # y : int
    # g : int
    # f : int
    # d : tuple[int,int]
    # b : tuple[tuple[int,int],int]
    # c : int
    # e : tuple[int,int]
    ((d,y),c) = a

    return 0

assert bad_function((1,2)) == 0
assert bad_function((3,2)) == 0
