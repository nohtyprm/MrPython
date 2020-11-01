##!FAIL: TupleTypeExpectationError[int]@11:4

def tuple_destruct(t : Tuple[int, int]) -> int:
    ''''''

    a : Tuple[int,int]
    a = (1,4)
    b: int
    c: int
    g: int
    ((b,c),g) = a
    return 0
