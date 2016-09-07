### A few error tests

## DivisionbyZero
#2//0

def div_zero(blu):
    return blu + 2 // 0

#div_zero(42)

## IndentationError
#if True:
#13

#def bad_indent(blo):
#    if True:
#    13
#    else:
#        return blo


## SyntaxError
#if 3 > 2 then:
#    pass

## NameError
#print(undef)

#def name_error_inside(bla):
#    return bla + bli

#name_error_inside(42)

## TypeError
#2 + "hello"

def type_error(bly):
    return 2 + bly

#type_error("hello")

## AssertionError
#assert True == False
