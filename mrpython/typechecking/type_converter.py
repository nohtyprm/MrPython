try:
    from .type_ast import *
except ImportError:
    from type_ast import *


def type_converter(annotation, ctx):
    if hasattr(annotation, "id"):
        if annotation.id == "int":
            return IntType(annotation)
        elif annotation.id == "bool":
            return BoolType(annotation)
        elif annotation.id == "str":
            return StrType(annotation)
        elif annotation.id == "float":
            return FloatType(annotation)
        else:
            return None
    elif hasattr(annotation, "slice"):
        types = []
        for i in annotation.slice.value.elts:
            types.append(type_converter(i))
        return TupleType(types)
    else:
        return None

def fun_converter(fun_def, ctx):
    param_types = []
    for par in fun_def.param_types:
        param_types.append(type_converter(par,ctx))
    ret_type = type_converter(fun_def.returns,ctx)

    return FunctionType(param_types,ret_type,False,1)

if __name__ == "__main__":
    import sys
    import prog_ast
    import type_ast
    prog1 = Program()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "../../examples/revstr.py"

    prog1.build_from_file(filename)

    converter = TypeConverter()
    typeAst = converter.parse(prog1)
