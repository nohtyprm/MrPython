##!FAIL: DuplicateMultiFunDeclarationError[f]@10:0

def f(a:int,b:int)->int:
    """ Retourne la somme de a et b"""
    #x:int
    #x:int

    return a+b

def f(a:int,b:int)->int:
    """ Retourne la soustraction de a et b"""
    #x:int
    #x:int

    return a-b


assert f(2,3)==5
