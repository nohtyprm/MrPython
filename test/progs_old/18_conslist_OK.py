##!FAIL:

def cons(x, l):
    """ alpha * list[alpha] -> list[alpha] """
    return [x] + l


assert cons(42, []) == [42]  # OK
assert cons(1, cons(2, [3, 4, 5])) == [1, 2, 3, 4, 5]  # OK


def nil():
    """ -> list[alpha] """
    return []

assert nil() == []  # OK
assert nil() == nil()  # does not terminate
assert cons(1, nil()) == [1]  # does not type-check
