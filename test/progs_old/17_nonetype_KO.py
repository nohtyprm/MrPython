##!FAIL: OptionCoercionWarning[int/int + NoneType]@15:15

def f(L):
    """ list[alpha] -> alpha + NoneType """

    if len(L) > 0:
        return L[0]

def g(L):
    """ list[int] -> int """
    # t : int + NoneType
    t = f(L)

    if t != None:
        return t  # put a coercion int(t) to remove the warning
    else:
        return 0

