from math import sqrt
# fonction
def prec_trinome(a : float , b : float , c : float ) -> float:
    """
     Précondition :  a < 0 
    """
    delta = b**2 - 4*a*c
    if delta > 0.0:
        racine_delta = sqrt(delta)
        return (2, (-b-racine_delta)/(2*a), (-b+racine_delta)/(2*a))
    elif delta < 0.0:
        return (0,)
    else:
        return (1, (-b/(2*a)))
        
 #jeu de test 
 assert prec_trinome(1.0, -3.0, 2.0) == (2, 1.0, 2.0)
 assert prec_trinome(1.0, -2.0, 1.0) == (1, 1.0)
  
