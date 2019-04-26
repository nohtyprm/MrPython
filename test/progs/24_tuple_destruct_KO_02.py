##!FAIL: UndeclaredVariableError[b]@9:5

def tuple_destruct(T):
    '''tuple[int,int] -> int'''

    #a : tuple[int,int]
    a = (1,4)
    #g: int
    (b,g) = a
    return 0
