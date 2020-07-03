##!FAIL: IteratorTypeError[int]@6:13

def f(s):
    """str -> int"""
    # i : int
    for i in len(s):
        pass

