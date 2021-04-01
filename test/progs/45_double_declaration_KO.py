##!FAIL: DuplicateMultiAssignError[x]@6:0

def f(a:int,b:int)->int:
    """ Retourne la somme de a et b"""
    x:int
    x:int

    return a+b

print(f(2,3))
