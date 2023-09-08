
def f(n : int) -> List[int]:
    """ """
    lst : List[int] = []
    for _ in range(0, n):
        lst.append(42)

    return lst

        
assert f(3) == [42, 42, 42]
