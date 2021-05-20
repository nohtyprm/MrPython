

def prec_f(l :Iterable[Tuple[float,Tuple[float,float,Tuple[float,float,float], float], float]]) -> float:
    """
       Précondition : l == []
    """

    a : float
    a = 0
    
    g : float
    e : float
    for (b, (c, d, (e, _, f), _), g) in l:
        a = a + b + c + d + e + f + g 

    return a


#              a   b   c   d   e   f   g
assert prec_f([(1, (2, 3, (4, 5, 6), 7), 8)
          ,(9, (10, 11, (12, 13, 14), 15), 15)]) == 95


