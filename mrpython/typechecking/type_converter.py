try:
    from .type_ast import *
except ImportError:
    from type_ast import *

def type_converter(annotation):
    if hasattr(annotation, "id"):
        print("cet attribut a une annotation id")
        if annotation.id == "int":
            return IntType(annotation)
        elif annotation.id == "bool":
            return BoolType(annotation)
        elif annotation.id == "str":
            return StrType(annotation)
        elif annotation.id == "float":
            print("progast marche")
            return FloatType(annotation)
    elif hasattr(annotation, "slice"):
        types = []
        for i in annotation.slice.value.elts:
            types.append(type_converter(i))
        return TupleType(types)
    else:
        print("annotation mal instanciée")
        # return "UnsupportedNode"
        return None

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
