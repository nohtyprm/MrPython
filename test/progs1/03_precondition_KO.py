
def prec_f(a:int,b:int)->int:
    """ Precondition : (a<0) and (b<0)"""

    return a+b

assert prec_f(2,3)==5
assert prec_f(10,3) != 10
