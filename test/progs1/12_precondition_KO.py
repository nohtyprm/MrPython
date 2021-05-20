
def prec_base_mult(base :float , debut : float , fin : float , inc: float ): -> float :
    """Affiche la table des <base>, de <debut> a <fin>, de <inc> en <inc>.
       Precondition : debut > fin
    """
     n = debut
     while n <= fin:
        print(n, 'x', base, '=', n*base)
        n = n + inc
     return n
           

# Jeu de tests
assert prec_base_mult(3,2,10,1) == 3
assert prec_base_mult(7,2,10,1) == 7

