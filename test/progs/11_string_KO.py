##!FAIL: UnknownTypeAliasError[string]@6:0

# remark : string type is "str" not "string"
# counter-example courtesy of wegank@github, thanks !

def f(x : int) -> string:
    """blabla"""

    return "test"


assert f(42) == "test"
assert f(12) == "test"

