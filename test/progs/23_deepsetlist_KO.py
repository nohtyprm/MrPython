##!FAIL: UnhashableElementError[List[int]]@14:7

def deepsetlist(l : List[List[T]]) -> List[Set[T]]:
    """ """
    ens : Set[T]
    ens = set()
    
    e : T
    for e in l[0]:
        ens.add(e)
    return [ens]


assert deepsetlist([[[1, 2], [3, 4]], []]) == [set()]  # boum !
