##!FAIL: SignatureTrailingError[f/ing]@6:0

# remark : string type is "str" not "string"
# counter-example courtesy of wegank@github, thanks !

def f(x):
    """ int -> string """

    return "test"


assert f(42) == "test"
assert f(12) == "test"

