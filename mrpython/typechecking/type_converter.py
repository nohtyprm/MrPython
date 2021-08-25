
import ast

try:
    from .type_ast import *
    from .translate import tr
except ImportError:
    from type_ast import *
    from translate import tr

def mk_container_type(container_id, element_value, annotation): 
    #import pdb ; pdb.set_trace()
    ok, element_type = type_converter(element_value)
    if not ok:
        return (False, element_type)

    if container_id == 'Sequence':
        return (True, SequenceType(element_type, annotation))
    elif container_id == 'List':
        return (True, ListType(element_type, annotation))
    elif container_id == 'Set':
        return (True, SetType(element_type, annotation))
    elif container_id == 'Optional':
        return (True, OptionType(element_type, annotation))
    elif container_id == 'Iterable':
        return (True, IterableType(element_type, annotation))
    else:
        return (False, tr("Unsupported container type: {}").format(container_id))

def mk_tuple_type(tuple_value, annotation):
    if hasattr(tuple_value, "elts"):    
        elem_types = []
        for elem_annot in tuple_value.elts:
            ok, elem_type = type_converter(elem_annot)
            if not ok:
                return (False, elem_type)
            elem_types.append(elem_type)
        return (True, TupleType(elem_types, annotation))
    else:
        return (False, tr("Does not understand the declared tuple type (missing element types)."))

def mk_dict_type(dict_value, annotation):
    if hasattr(dict_value, "elts"):    
        elem_types = []
        for elem_annot in dict_value.elts:
            ok, elem_type = type_converter(elem_annot)
            if not ok:
                return (False, elem_type)
            elem_types.append(elem_type)
        if len(elem_types) != 2:
            return (False, tr("A dictionnary type must have two arguments: the key type and the value type"))
        return (True, DictType(elem_types[0], elem_types[1], annotation))
    else:
        return (False, tr("Does not understand the declared dictionary type (missing key/value types)."))
        

def callable_type_converter(annot, param_annots, ret_annot):
    param_types = []
    for param_annot in param_annots:
        ok, ty = type_converter(param_annot)
        if not ok:
            return ok, ty
        param_types.append(ty)

    ok, ret_type = type_converter(ret_annot)
    if not ok:
        return ok, ret_type

    return (True, FunctionType(param_types, ret_type, partial=False, annotation=annot))

def type_converter(annotation):
    #import astpp
    #print(astpp.dump(annotation))

    #import pdb ; pdb.set_trace()
    # Special case for function types (HOF)
    if hasattr(annotation, "value") and hasattr(annotation.value, "id") and annotation.value.id == "Callable":
        sig = annotation.slice.value.elts
        if len(sig) != 2:
            return (False, tr("Callable format error, expect 2 arguments"))

        return callable_type_converter(annotation, sig[0].elts, sig[1])
    
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
        elif annotation.id in { 'range', 'Range' }:
            return (True, SequenceType(IntType(), annotation))
        elif annotation.id == "Image":
            return (True, ImageType(annotation))
        elif annotation.id == "Number":
            return (False, tr("the `{}` type is deprecated, use `{}` instead").format('Number', 'float'))
        elif annotation.id == "NoneType":
            return (False, tr("the `{}` type is deprecated, use `{}` instead").format('NoneType', 'None'))
        elif annotation.id in PREDEFINED_TYPE_VARIABLES:
            return (True, TypeVariable(annotation.id, annotation))
        else:
            return (True, TypeAlias(annotation.id, annotation))
    elif hasattr(annotation, "slice"):
        #import astpp
        #print("type annot = {}".format(astpp.dump(annotation)))
        if hasattr(annotation.value, "id"):
            #import pdb ; pdb.set_trace()
            container_id = annotation.value.id
            container_detail = fetch_container_detail(annotation)
            if container_id == "Tuple":
                return mk_tuple_type(container_detail, annotation)
            elif container_id == "Dict":
                if hasattr(annotation.slice, "lower") or hasattr(annotation.slice, "upper"):
                    return (False, tr("The colon ':' separator is not allower in dictionnary types, use ',' instead"))
                elif hasattr(annotation.slice, "value"):
                    return mk_dict_type(container_detail, annotation)
                else:
                    return (False, tr("Missing key,value types in dictionnary type")) 
            else:
                return mk_container_type(container_id, container_detail, annotation)
        
        return (False, tr("Does not understand the declared container type."))
    else:
        return (False, tr("Does not understand the declared type."))

def fetch_container_detail(annotation):
    if isinstance(annotation.slice, ast.Index):
        # Python <= 3.8  for lists, ...
        return annotation.slice.value
    elif isinstance(annotation.slice, (ast.Subscript, ast.Tuple, ast.Slice, ast.Name)):
        # Python >= 3.9  or >= 3.8 (for dicts)
        return annotation.slice

    raise ValueError("wrong annotation (please report)")

def check_if_roughly_type_expr(annotation):
    ### XXX : this is *very* rough !
    if hasattr(annotation, "id") and annotation.id in {"int", "bool", "str", "float"} | PREDEFINED_TYPE_VARIABLES:
        return True
    elif hasattr(annotation, "slice") and hasattr(annotation.value, "id") \
         and annotation.value.id in {"Tuple", "List", "Iterable", "Set", "Sequence", "Dict" }:
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
