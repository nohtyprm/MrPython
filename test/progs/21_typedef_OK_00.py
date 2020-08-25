
Personne = Tuple[str, str, int, bool]

def est_majeure(p : Personne) -> bool:
    """Renvoie True si la personne est majeure, ou False sinon."""

    nom, pre, age, mar = p
    
    return age >= 18

# jeu de tests
assert est_majeure(('Itik', 'Paul', 17, False)) == False
assert est_majeure(('Unfor', 'Marcelle', 79, True)) == True

