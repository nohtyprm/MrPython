def maximum(a : float, b : float) -> float:
    mini : float
    maxi : float
    if a < b:
      mini = a
      maxi = b
    else:
      mini = b
      maxi = a

    return maxi

# Jeu de tests
assert maximum(2, 5) == 5
assert maximum(5, 2) == 5
assert maximum(3, 3) == 3
