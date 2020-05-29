# Exercice 1.2 : Calcul d'un prix TTC

## Question 1

def prix_ttc(prix : float, taux : float) -> float:
    """Hypothèse : prix >= 0
    Retourne le prix TTC correspondant au prix HT 'prix'
    avec un taux de TVA 'taux'
    """
    return prix * (1 + taux / 100.0)

# Jeu de tests
assert prix_ttc(100.0, 20.0) == 120.0
assert prix_ttc(100, 0.0) == 100.0
assert prix_ttc(100, 100.0) == 200.0
assert prix_ttc(0, 20) == 0.0
assert prix_ttc(200, 5.5) == 211.0


## Question 2

def prix_ht(prix : float, taux : float) -> float:
    """Retourne le prix HT correspondant au prix TTC 'prix'
    avec un taux de TVA 'taux'
    """
    return prix / (1 + taux / 100.0)

# Jeu de tests
assert prix_ht(120, 20) == 100.0
assert prix_ht(100, 0) == 100.0
assert prix_ht(200, 100) == 100.0
assert prix_ht(0, 20) == 0.0
assert prix_ht(211, 5.5) == 200.0
