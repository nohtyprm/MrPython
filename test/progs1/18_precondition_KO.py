def bad_function(t : Tuple[int, int]) -> int:
    
    """
      Precondition : t == 2.0
      
    """

    a : Tuple[Tuple[int,int],int]
    a = ((1,2),4)
    d : Tuple[int,int]
    g: int
    (d,g) = a
    return 0

assert bad_function((1,2)) == 0
assert bad_function((3,2)) == 0
