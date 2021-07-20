
def incrementer(d : Dict[str,int]) -> None:
    """Incrémente tous les éléments du dictionnaire d.
    """
    e : str
    for e in d:
        d[e] = d[e] + 1

# Jeu de tests

MonDict : Dict[str, int] = {"1st":1, "2nd":2, "3rd":3, "4th":4, "5th":5, "6th":6}

assert incrementer(MonDict) == None
assert MonDict == {"1st":2, "2nd":3, "3rd":4, "4th":5, "5th":6, "6th":7}


