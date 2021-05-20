def tata(x: str, n: int) -> List[str]:
    """ 
      precondition : (n == "x") and (x == 1)
     """
    # l: list[str]
    l : List[str] = [x]*n
    return l

assert tata("test", 2) == ["test", "test"]
