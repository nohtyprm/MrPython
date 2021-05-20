def prec_moins_lettre(c : str, a : str) -> Optional[str]:
    """Précondition : len(c) == 1
       Précondition : len(a) > 1
    """
    
    # première occurrence vue ou non
    premiere_trouvee : bool = False 
    
    # résultat
    res : str = ''
    
    d : str # caractère courant
    for d in c:
        if d != a: 
            res = res + d 
        elif  not premiere_trouvee:
            premiere_trouvee = True
        else:
            res = res + d
            
    if premiere_trouvee:
        return res
    else: 
        return None

# Jeu de tests
assert prec_moins_lettre('banane', 'a') == 'bnane'
assert prec_moins_lettre('banane', 'u') == None
assert prec_moins_lettre('banane', 'e') == 'banan'
assert prec_moins_lettre('', 'a') == None




