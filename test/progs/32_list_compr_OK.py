def triplets(n : int) -> List[Tuple[int, int, int]]:
    """Précondition : n >= 0
    Retourne la liste des triplets (i,j,k) sur l'intervalle [1;n]."""

    return [(i, j, k) for i in range(1, n+1)
                      for j in range(1, n+1)
                      for k in range(1, n+1)]

# Jeu de tests
assert triplets(0) == []
assert triplets(1) == [(1, 1, 1)]
assert triplets(2) == [(1, 1, 1),
                       (1, 1, 2),
                       (1, 2, 1),
                       (1, 2, 2),
                       (2, 1, 1),
                       (2, 1, 2),
                       (2, 2, 1),
                       (2, 2, 2)]

def decompositions(n : int) -> List[Tuple[int, int, int]]:
    """Précondition : n >= 0
    Retourne la liste des triangles sur l'intervalle [1;n]."""
    
    return [(i, j, k) for i in range(1, n+1)
                      for j in range(1, n+1)
                      for k in range(1, n+1) if i + j == k]    

# Jeu de tests
assert decompositions(0) == []
assert decompositions(1) == []
assert decompositions(2) == [(1, 1, 2)]
assert decompositions(3) == [(1, 1, 2), (1, 2, 3), (2, 1, 3)]
assert decompositions(4) == [(1, 1, 2), (1, 2, 3), (1, 3, 4), 
                             (2, 1, 3), (2, 2, 4), (3, 1, 4)]

def decompositions_bis(n : int) -> List[Tuple[int, int, int]]:
    """Précondition : n >= 0
    Retourne la liste des triangles sur l'intervalle [1;n]."""
    
    return [(i, j, i+j) for i in range(1, n+1)
                        for j in range(1, n+1) if i+j<=n]

# Jeu de tests
assert decompositions_bis(0) == []
assert decompositions_bis(1) == []
assert decompositions_bis(2) == [(1, 1, 2)]
assert decompositions_bis(3) == [(1, 1, 2), (1, 2, 3), (2, 1, 3)]
assert decompositions_bis(4) == [(1, 1, 2), (1, 2, 3), (1, 3, 4), 
                             (2, 1, 3), (2, 2, 4), (3, 1, 4)]


def encadrements(n : int) -> List[Tuple[int, int, int]]:
    """Précondition : n >= 0
    Retourne la liste des triplets (i,j,k) sur l'intervalle [1;n]
    tels que i<=j<=k."""
    
    return [(i, j, k) for i in range(1, n+1)
                      for j in range(i, n+1)
                      for k in range(j, n+1)]    

# Jeu de tests
assert encadrements(0) == []
assert encadrements(1) == [(1, 1, 1)]
assert encadrements(2) == [(1, 1, 1), (1, 1, 2), (1, 2, 2), (2, 2, 2)]
assert encadrements(3) == [(1, 1, 1),
                           (1, 1, 2),
                           (1, 1, 3),
                           (1, 2, 2),
                           (1, 2, 3),
                           (1, 3, 3),
                           (2, 2, 2),
                           (2, 2, 3),
                           (2, 3, 3),
                           (3, 3, 3)]

def encadrements_bis(n : int) -> List[Tuple[int, int, int]]:
    """... """
    
    return [(i, j, k) for i in range(1, n+1)
                      for j in range(1, n+1)
                      for k in range(1, n+1) if (i <= j) and (j <= k)]

# Jeu de tests
assert encadrements_bis(0) == encadrements(0)
assert encadrements_bis(1) == encadrements(1)
assert encadrements_bis(2) == encadrements(2)
assert encadrements_bis(3) == encadrements(3)

def encadrements3(n : int) -> List[Tuple[int, int, int]]:
    """Précondition : n >= 0
    Retourne la liste des triplets (i,j,k) sur l'intervalle [1;n]
    tels que i<=j<=k."""
    
    L : List[Tuple[int, int, int]]
    L = []  # liste résultat
    
    nb_tours : int
    nb_tours = 0  # nombre de tours de boucle (en TME)
    
    i : int
    for i in range(1, n+1):
        
        j : int
        for j in range(i, n+1):
            
            k : int
            for k in range(j, n+1):
                nb_tours = nb_tours + 1  # en TME
                
                L.append((i, j, k))


    print('Nombre de tours de boucles =', nb_tours)  # en TME
    return L

def encadrements_bis3(n : int) -> List[Tuple[int, int, int]]:
    """ ... """
    
    L : List[Tuple[int, int, int]]
    L = []  # liste résultat
    
    nb_tours : int
    nb_tours = 0  # nombre de tours de boucle (en TME)

    i : int
    for i in range(1, n+1):
        
        j : int
        for j in range(1, n+1):
            
            k : int
            for k in range(1, n+1):
                nb_tours = nb_tours + 1 # en TME
                if (i <= j) and (j <= k):
                    L.append((i, j, k))

                
    print('Nombre de tours de boucles =', nb_tours)  # en TME
    return L
