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

def mk_tuple_type(tuple_value, annotation):
    if hasattr(annotation.slice.value, "elts"):    
        elem_types = []
        for elem_annot in annotation.slice.value.elts:
            ok, elem_type = type_converter(elem_annot)
            if not ok:
                return (False, elem_type)
            elem_types.append(elem_type)
        return (True, TupleType(elem_types))
    else:
        return (False, tr("Does not understand the declared tuple type (missing element types)."))
        
def type_converter(annotation):
    #import astpp
    #print(astpp.dump(annotation))

    # Special case for None/NoneType
    if hasattr(annotation, "value") and annotation.value == None:
        return (True, NoneTypeType(annotation))
    
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
            return (False, tr("the `{}` type is deprecated, use `{}` instead").format('Number', 'float'))
        elif annotation.id == "NoneType":
            return (False, tr("the `{}` type is deprecated, use `{}` instead").format('NoneType', 'None'))
        elif annotation.id in PREDEFINED_TYPE_VARIABLES:
            return (True, TypeVariable(annotation.id, annotation))
        else:
            return (True, TypeAlias(annotation.id, annotation))
    elif hasattr(annotation, "slice"):
        # import astpp
        # print("type annot = {}".format(astpp.dump(annotation)))
        if hasattr(annotation.value, "id"):
            container_id = annotation.value.id
            if container_id == "Tuple":
                return mk_tuple_type(annotation.slice.value, annotation)
            else:
                return mk_container_type(container_id, annotation.slice.value, annotation)
        else:
            return (False, tr("Does not understand the declared container type."))
    else:
        return (False, tr("Does not understand the declared type."))

def check_if_roughly_type_expr(annotation):
    ### XXX : this is *very* rough !
    if hasattr(annotation, "id") and annotation.id in {"int", "bool", "str", "float"} | PREDEFINED_TYPE_VARIABLES:
        return True
    elif hasattr(annotation, "slice") and hasattr(annotation.value, "id") \
         and annotation.value.id in {"Tuple", "List", "Iterable", "Sequence", "Dict" }:
        return True
    else:
        return False

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
