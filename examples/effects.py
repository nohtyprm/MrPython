


def mk_list(n):
    """ int -> list[int] """

    return [k for k in range(1, n+1)]

assert mk_list(3) == [1, 2, 3]
assert mk_list(5) == [1, 2, 3, 4, 5]


def mon_append_ok(L, e):
    """ list[alpha] * alpha -> list[alpha]
    retourne la liste L avec l'élément e à la fin. """

    return L + [e]

# ListeGlobale : list[int]
ListeGlobale = [1, 2, 3]

assert mon_append_ok(mk_list(3), 4) == [1, 2, 3, 4]
assert mon_append_ok(mon_append_ok(mk_list(3), 4), 5) == [1, 2, 3, 4, 5]
assert mon_append_ok(ListeGlobale, 4) == [1, 2, 3, 4]
assert mon_append_ok(ListeGlobale, 4) == [1, 2, 3, 4]

assert mon_append_ok(mon_append_ok(ListeGlobale, 4), 5) == [1, 2, 3, 4, 5]


def mon_append_ko(L, e):
    """ list[alpha] * alpha -> list[alpha]
    retourne la liste L avec l'élément e à la fin. """

    L.append(e)  # Erreur : effet de bord non-contrôlé sur la liste L
    return L

assert mon_append_ko(mk_list(3), 4) == [1, 2, 3, 4]
assert mon_append_ko(mon_append_ko(mk_list(3), 4), 5) == [1, 2, 3, 4, 5]
assert mon_append_ko(ListeGlobale, 4) == [1, 2, 3, 4]
assert mon_append_ko(ListeGlobale, 4) == [1, 2, 3, 4]

#assert mon_append_ko(mon_append_ko(ListeGlobale, 4), 5) == [1, 2, 3, 4, 5]


## Question: interdire l'aliasing ? 




