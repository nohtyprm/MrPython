##!FAIL: GlobalVariableUseError[glob]@12:18

glob : Dict[str,int] = {"test": 1}
assert glob["test"] == 1

def f(lst:List[str])-> Dict[str,float]:
    """..."""
    l : int = len(lst)
    dic : Dict[str,float] = dict()
    e:str
    for e in lst:
        dic[e] = (glob[e]/l)
    return dic

