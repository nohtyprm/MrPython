##!FAIL: TupleTypeExpectationError[int]@11:5

def tuple_destruct(T):
    '''tuple[int,int] -> int'''

    #a : tuple[int,int]
    a = (1,4)
    #b: int
    #c: int
    #g: int
    ((b,c),g) = a
    return 0
