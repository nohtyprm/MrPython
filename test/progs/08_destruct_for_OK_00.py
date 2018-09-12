

def f(L):
    """ Iterable[Tuple[Number,Tuple[Number,Number,Tuple[Number,Number,Number], Number], Number]] -> Number """

    # a : Number
    a = 0
    
    # g : Number
    # e : Number
    for (b, (c, d, (e, _, f), _), g) in L:
        a = a + b + c + d + e + f + g 

    return a


#              a   b   c   d   e   f   g
assert f([(1, (2, 3, (4, 5, 6), 7), 8)
          ,(9, (10, 11, (12, 13, 14), 15), 15)]) == 42


