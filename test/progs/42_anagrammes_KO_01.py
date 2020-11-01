##!FAIL: OptionCoercionWarning[str/str + NoneType]@55:18

def moins_lettre(c : str, a : str) -> Optional[str]:
    """Précondition : len(c) == 1
    Retourne le mot c privé de la première occurrence du caractère a
             si c contient a, ou None sinon.
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
assert moins_lettre('banane', 'a') == 'bnane'
assert moins_lettre('banane', 'u') == None
assert moins_lettre('banane', 'e') == 'banan'
assert moins_lettre('', 'a') == None


## Question 2 - Mots anagrammes

def anagramme(m1 : str, m2 : str) -> bool:
    """Renvoie True quand les mots m1 et m2 sont anagrammes, 
            ou False sinon.
    """ 
    
    # copie de m2 à laquelle on va retirer des lettres
    cm2 : str = m2
    
    # résultat de la fonction moins_lettre
    res : Optional[str] = None
    
    a : str
    for a in m1:
        res = moins_lettre(cm2, a) # on essaye de retirer a dans la copie courante de m2, cm2
        if res == None: # si on n'a pas pu (car cm2 ne contient pas res)
            return False # m1 et m2 ne peuvent etre anagrammes 
        else: # sinon
            cm2 = res  # cm2 devient l'ancienne cm2 sans la lettre a
            
    return (cm2 == '') # en fin de boucle on vérifie que toutes les lettres ont été
                       # enlevées. On rend donc True s'il ne reste rien dans cm2 
                       # (cela signifiant que tout à été enlevé) ou False sinon.


# Jeu de tests
assert anagramme("alberteinstein", "alberteinstein") == True
assert anagramme("alberteinstein", "riennestetabli") == True
assert anagramme("alberteinstein", "toutestrelatif") == False
assert anagramme("lagravitationuniverselle", "loivitaleregnantsurlavie") == True
assert anagramme("lesfeuxdelamour", "dramesexuelflou") == True
assert anagramme("iamlordvoldemort", "tommarvoloriddle") == True
assert anagramme("iamharrypotter", "tommarvoloriddle") == False
