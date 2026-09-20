def positif(a : int) -> int:
    """Retourne a, qui doit être positif.
       Précondition : a >= 0
    """
    return a

def petit_positif(b : int) -> int:
    """Retourne b, qui doit être positif et petit.
       Précondition : b <= 10
    """
    return positif(b)

# Jeu de tests
assert positif(1) == 1
assert petit_positif(1) == 1
assert petit_positif(10) == 10
