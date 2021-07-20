
def fmap(f : Callable([T], U), lst : List[T]) -> List[U]:
    """
    """
    return [f(e) for e in lst]


# Jeu de tests
def incr(n : int) -> int:
    """ """
    return + 1

assert fmap(incr, []) == []
assert fmap(incr, [1, 2, 3, 4]) == [2, 3, 4, 5]

