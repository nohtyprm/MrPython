##!FAIL: UnhashableElementError[List[int]]@14:7

def setlist(l : List[T]) -> Set[T]:
    """"""
    ens : Set[T]
    ens = set()
    
    e : T
    for e in l:
        ens.add(e)
    return ens


assert setlist([[1, 2], [3, 4]]) == set()  # boum !
