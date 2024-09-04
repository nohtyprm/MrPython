##!FAIL: Erreur: ligne 21

import math

def trinome(a : float , b : float , c : float ) -> Tuple[int, float, float]:
    """
     Précondition :  a != 0 
    """
    delta : float
    delta = b**2 - 4*a*c
    if delta > 0.0:
        racine_delta : float
        racine_delta = math.sqrt(delta)
        return (2, (-b-racine_delta)/(2*a), (-b+racine_delta)/(2*a))
    elif delta < 0.0:
        return (0, 0, 0)
    else:
        return (1, (-b/(2*a)), (-b/(2*a)))
        
 #jeu de test 
assert trinome(0, -3.0, 2.0) == (2, 1.0, 2.0)
assert trinome(1.0, -2.0, 1.0) == (1, 1.0, 1.0)
  
