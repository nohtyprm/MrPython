try:
    from .type_ast import *
    from .translate import tr
except ImportError:
    from type_ast import *
    from translate import tr

def mk_container_type(container_id, element_value, annotation):
    ok, element_type = type_converter(element_value)
    if not ok:
        return (False, element_type)

    if container_id == 'Sequence':
        return (True, SequenceType(element_type, annotation))
    elif container_id == 'List':
        return (True, ListType(element_type, annotation))
    elif container_id == 'Iterable':
        return (True, IterableType(element_type, annotation))
    else:
        return (False, tr("Unsupported container type: {}").format(container_id))

def type_converter(annotation):
    if hasattr(annotation, "id"):
        if annotation.id == "int":
            return (True, IntType(annotation))
        elif annotation.id == "bool":
            return (True, BoolType(annotation))
        elif annotation.id == "str":
            return (True, StrType(annotation))
        elif annotation.id == "float":
            return (True, FloatType(annotation))
        elif annotation.id == "Number":
            return (False, tr("the `Number` type is deprecated, use `float` instead"))
        elif annotation.id in PREDEFINED_TYPE_VARIABLES:
            return (True, TypeVariable(annotation.id, annotation))
        else:
            return (True, TypeAlias(annotation.id, annotation))
    elif hasattr(annotation, "slice"):
        if hasattr(annotation.value, "id"):
            container_id = annotation.value.id
            return mk_container_type(container_id, annotation.slice.value, annotation)
        elif hasattr(annotation.slice.value, "elts"):    
            types = []
            for i in annotation.slice.value.elts:
                types.append(type_converter(i))
            return (True, TupleType(types))
        else:
            return (False, tr("Does not understand the declared type."))

def fun_type_converter(fun_def):
    param_types = []
    for (par, par_type) in zip(fun_def.parameters, fun_def.param_types):
        ok, ret_type = type_converter(par_type)
        if not ok:
            return (False, tr("Parameter '{}': {}").format(par, ret_type))

        param_types.append(ret_type)
        
    ok, ret_type = type_converter(fun_def.returns)
    if not ok:
        return (False, tr("Return type: {}").format(ret_type))

    return (True, FunctionType(param_types,ret_type,False,1))

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
