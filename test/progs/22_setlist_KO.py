##!FAIL: UnhashableElementError[list[int]]@13:7

def setlist(L):
    """ list[alpha] -> set[alpha] """
    # E : set[alpha]
    E = set()
    # e : alpha
    for e in L:
        E.add(e)
    return E


assert setlist([[1, 2], [3, 4]]) == set()  # boum !
