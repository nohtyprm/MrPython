### A few error tests

## DivisionbyZero
#2//0

## IndentationError
#if True:
#13

## SyntaxError
#if 3 > 2 then:
#    pass

## NameError
#print(undef)

def name_error_inside(bla):
    return bla + bli

name_error_inside(42)

## TypeError
#2 + "hello"

## AssertionError
#assert True == False
