##!FAIL: Erreur: ligne 8

def addition(a:int,b:int)->int:
    """ HyPoThEsE : (a > 0) and (b > 0)"""

    return a + b

assert addition(-2,3) == 1
assert addition(10,3) != 10
