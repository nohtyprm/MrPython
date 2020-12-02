##!FAIL: OptionCoercionWarning[Tuple[int,List[int]]/Optional[Tuple[int,List[int]]]]@5:4

def f(t : Optional[Tuple[int, List[int]]]) -> int:
    """"""
    n, l = t
    return n


assert f((42, [1, 2, 3])) == 42
assert f((42, [1, 2])) == 42
