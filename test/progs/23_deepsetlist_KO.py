##!FAIL: UnhashableElementError[list[int]]@13:7

def deepsetlist(L):
    """ list[list[alpha]] -> list[set[alpha]] """
    # E : set[alpha]
    E = set()
    # e : alpha
    for e in L[0]:
        E.add(e)
    return [E]


assert deepsetlist([[[1, 2], [3, 4]], []]) == [set()]  # boum !
