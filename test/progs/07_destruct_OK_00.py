

def f(a):
    """ Number -> Number """

    # g : Number
    # e : Number
    b, (c, d, (e, _, f), _), g = (a, (2, 3, (4, 5, 6), 7), 8)

    return a + b + c + d + e + f + g


#              a   b   c   d   e   f   g
assert f(1) == 1 + 1 + 2 + 3 + 4 + 6 + 8

