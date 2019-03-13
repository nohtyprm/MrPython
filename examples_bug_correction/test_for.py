def f(L):
    """list[int]->int"""
    #s: str
    s = "a"
    #e: int
    for e in L:
        print(str(e) + " " + str(s))

    __type_check(s)
    return 0

assert f([1, 2, 3]) == 0
