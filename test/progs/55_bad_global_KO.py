##!FAIL: VariableTypeError[prenom:str/int]@5:0

test : Tuple[str, int] = ("Maxime", 23)
prenom : int
prenom, age = test

