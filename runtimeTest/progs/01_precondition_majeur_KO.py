##!FAIL: Erreur: ligne 6

def est_majeure(nom: str, prenom : str, age: int) -> bool:
    """
       Renvoie True si la personne est majeure, ou False sinon.
       Précondition : nom != "" and prenom != "" and age > 0 
    """
    return age >= 18

# jeu de tests
assert est_majeure('Itik', 'Paul', 17) == False
assert est_majeure('Unfor', 'Marcelle', (-1)) == True

