def tata(x: str, n: int) -> List[str]:
    """ rien """
    # l: list[str]
    l : List[str] = [x]*n
    return l

assert tata("test", 2) == ["test", "test"]
