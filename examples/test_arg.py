def test_args(x,y):
    """
    Number * Number -> Number
    Hyp : empty
    return the sum of x and y 
    """
    return x+y

assert test_args(1,2) == 3
assert test_args(1.5,22,5) == 24
