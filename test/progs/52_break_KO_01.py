##!FAIL: DeclarationWarning[var-name]@7:8

def test(s : str) -> str:
    """"""

    # c : str
    for c in s:
        print(c)
        break
    return s

print(test("aaa"))
