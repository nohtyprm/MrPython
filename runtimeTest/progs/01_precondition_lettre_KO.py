##!FAIL: Erreur: ligne 5

def moins_lettre(m : str, c : str) -> Optional[str]:
    """
        Précondition : len(m) > 1
        Précondition : len(c) == 1
    """
    
    # première occurrence vue ou non
    premiere_trouvee : bool = False 
    
    # résultat
    res : str = ''
    
    d : str # caractère courant
    for d in m:
        if d != c: 
            res = res + d 
        elif not premiere_trouvee:
            premiere_trouvee = True
        else:
            res = res + d
            
    if premiere_trouvee:
        return res
    else: 
        return None

# Jeu de tests
assert moins_lettre('banane', 'a') == 'bnane'
assert moins_lettre('banane', 'u') == None
assert moins_lettre('banane', 'e') == 'banan'
assert moins_lettre('', 'a') == None




