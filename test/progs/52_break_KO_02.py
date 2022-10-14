##!FAIL: UnsupportedNodeError[Break]@9:8

def test(s : str) -> str:
    """"""

    c : str
    for c in s:
        print(c)
        break
    return s

print(test("aaa"))
