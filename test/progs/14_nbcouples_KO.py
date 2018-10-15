##!FAIL: IterVariableInEnvError[i]@11:8

def nb_couple_divise(n,p):
    """int * int -> int
    hyp : n <= p
    retourne le nombre de couple entier pour n divise p"""
    #somme : int
    somme = 0
    #i : int
    i = 0
    for i in range(n,p):
         #j : int  
         for j in range(n,p):
            if i%j == 0:
                 somme = somme +1
    return somme

