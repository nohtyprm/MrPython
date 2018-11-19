##!FAIL: ContainerAssignTypeError[str]@7:4

def f():
    """ -> NoneType """
    # s : str
    s = 'hello'
    s[0] = 'H'


assert f() == None
