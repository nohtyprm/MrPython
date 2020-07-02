# Exercice 1.3 : Calcul de fonctions polynômiales

## Question 1

def polynomiale(a : int, b : int, c  : int, d : int, x : int) -> int:
    """Retourne la valeur de a*x^3 + b*x^2 + c*x + d
    """
    return (a*x*x*x + b*x*x + c*x + d)

# Jeu de tests
assert polynomiale(1,1,1,1,2) == 15
assert polynomiale(1,1,1,1,3) == 40
assert polynomiale(2,0,0,0,1) == 2
assert polynomiale(0,3,0,0,1) == 3
assert polynomiale(0,0,4,0,1) == 4
assert polynomiale(1,2,3,4,0) == 4
assert polynomiale(2,3,4,5,1) == 14

def polynomiale2(a : int, b : int, c : int, d  : int, x : int) -> int:
    """Retourne la valeur de a*x^3 + b*x^2 + c*x + d
    """
    return (((((a*x + b) * x) + c) * x) + d)

# Jeu de tests
assert polynomiale2(1,1,1,1,2) == 15
assert polynomiale2(1,1,1,1,3) == 40
assert polynomiale2(2,0,0,0,1) == 2
assert polynomiale2(0,3,0,0,1) == 3
assert polynomiale2(0,0,4,0,1) == 4
assert polynomiale2(1,2,3,4,0) == 4
assert polynomiale2(2,3,4,5,1) == 14


## Question 2

def polynomiale_carre(a : int, b : int, c : int, x : int) -> int:
    """Retourne la valeur de a*x^4 + b*x^2 + c
    """
    return (a*x*x*x*x + b*x*x + c)

# Jeu de tests
assert polynomiale_carre(1,1,1,2) == 21
assert polynomiale_carre(1,1,1,3) == 91
assert polynomiale_carre(2,0,0,1) == 2
assert polynomiale_carre(0,3,0,1) == 3
assert polynomiale_carre(2,3,4,0) == 4
assert polynomiale_carre(2,3,4,1) == 9

def polynomiale_carre2(a : int,b : int, c : int, x : int) -> int:
    """Retourne la valeur de a*x^4 + b*x^2 + c
    """
    return (((a*x*x + b) * x*x) + c)

# Jeu de tests
assert polynomiale_carre2(1,1,1,2) == 21
assert polynomiale_carre2(1,1,1,3) == 91
assert polynomiale_carre2(2,0,0,1) == 2
assert polynomiale_carre2(0,3,0,1) == 3
assert polynomiale_carre2(2,3,4,0) == 4
assert polynomiale_carre2(2,3,4,1) == 9
