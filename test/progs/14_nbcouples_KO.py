##!FAIL: IterVariableInEnvError[i]@12:8

def nb_couple_divise(n : int,p : int) -> int:
    """précondition : n <= p
    Retourne le nombre de couple entier pour n divise p"""

    somme : int
    somme = 0

    i : int
    i = 0
    for i in range(n,p):
         j : int  
         for j in range(n,p):
            if i%j == 0:
                 somme = somme +1
    return somme

