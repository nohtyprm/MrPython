##!FAIL: OptionCoercionWarning[tuple[int,List[int]]/tuple[int,List[int]] + NoneType]@5:4

def f(t : Optional[Tuple[int, List[int]]]) -> int:
    """"""
    n, l = t
    return n


assert f((42, [1, 2, 3])) == 42
