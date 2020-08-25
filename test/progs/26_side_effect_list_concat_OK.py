def side_effect(l : List[int]) -> int:
    """"""
    l2 : List[int]
    l2 = l + []
    l2.append(2)
    return 0
