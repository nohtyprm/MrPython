
def fmap(f : Callable[[T], U], lst : List[T]) -> List[U]:
    """
    """
    return [f(e) for e in lst]

def fmap2(f : Callable[[T], U], lst: List[T]) -> List[U]:
    """
    """
    rlst : List[U] = []
    e : T
    for e in lst:
        rlst.append(f(e))
    return rlst


# Jeu de tests
def incr(n : int) -> int:
    """ """
    return n + 1

assert incr(0) == 1

assert fmap(incr, []) == []
assert fmap2(incr, []) == []
assert fmap(incr, [1, 2, 3, 4]) == [2, 3, 4, 5]
assert fmap2(incr, [1, 2, 3, 4]) == [2, 3, 4, 5]

def even(n : int) -> bool:
    """ """
    return (n % 2) == 0

assert even(1) == False
assert even(2) == True

assert fmap(even, [1, 2, 3, 4]) == [False, True, False, True]
assert fmap2(even, [1, 2, 3, 4]) == [False, True, False, True]

assert fmap(even, fmap(incr, [1, 2, 3, 4])) == [True, False, True, False]
assert fmap2(even, fmap2(incr, [1, 2, 3, 4])) == [True, False, True, False]
