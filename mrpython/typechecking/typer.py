import ast
from mrpython.typechecking.warnings import *
from mrpython.typechecking.type_annotation_parser\
    import TypeAnnotationParser
from typing import NamedTuple
from enum import Enum

class AssignAggregator(ast.NodeVisitor):
    def __init__(self):
        self.func_name = '__main__'
        self.assigns = {'__main__': []}
        self.warnings = []

    def visit_Assign(self, node):
        self.assigns[self.func_name].append(node)

    def visit_FunctionDef(self, node):
        self.func_name = node.name
        self.assigns[self.func_name] = []
        self.generic_visit(node)

class Type():
    def __init__(self, kind, lineno=None):
        self.kind = kind
        # Useful for parse information
        self.lineno = lineno

    def __eq__(self, other):
        '''This is defined as type equity - as defined by the kind string'''
        return self.kind == other.kind

    def class_eq(self, other):
        ''' '''
        return self.kind == self.kind and\
        self.lineno == other.lineno

    def is_of(self, kind):
        return self.kind == kind

    def __repr__(self):
        res = "Type(\"" + self.kind + "\""
        if self.lineno:
            res += ", " + str(self.lineno)
        return res + ")"

class TypeEnum(Enum):
    BOOL = 1
    INT = 2


class FunctionType():
    ''' We don't need to be recursive as there is no
        higher order functions in python 103.
    '''
    def __init__(self, params, ret):
        self.params = params
        self.ret = ret

class TypecheckResult(NamedTuple):
    type_dict: dict
    warnings: list

def get_annotations_from_ast(tree, codelines):
    ''' ast -> string list -> TypeCheckedResult(dict[str, dict[str, Type]], warnings list))
        Returns a dictionary of type information from an
        ast and a list of lines of code. The latter is needed
        in order to get back the annotation.
    '''
    type_dict = {}
    parser = TypeAnnotationParser()
    walker = AssignAggregator()
    walker.visit(tree)
    # Get warnings processed by the visitor
    warnings = walker.warnings
    for func_name in walker.assigns:
        type_dict[func_name] = {}
        for assign in walker.assigns[func_name]:
            assign_id = assign.targets[0].id
            lineno = assign.lineno
            # FIXME: This probably shouldn't be processed here
            if len(assign.targets) > 1:
                warnings.append(MultipleAssignment(lineno))

            parse_result = parser.parse_from_string(codelines[lineno - 2])
            if not parse_result.iserror:
                var_type = Type(parse_result.content.type, lineno - 1)
                var_id = parse_result.content.name
                # Annotation id different from assign id
                if (assign_id != var_id):
                    warn = WrongAnnotation(assign_id, var_id, lineno - 1)
                    warnings.append(warn)

                # Duplicate annotation warning
                if var_id in type_dict[func_name].keys():
                    first_lineno = type_dict[func_name][var_id].lineno
                    warn = DuplicateAnnotation(var_id, first_lineno, lineno - 1)
                    warnings.append(warn)

                type_dict[func_name][var_id] = var_type
            # Variable not annoted warning
            for var in assign.targets:
                if var.id not in type_dict[func_name]:
                    warnings.append(TypeAnnotationNotFound(var.id, assign.lineno))

    return TypecheckResult(type_dict, warnings)

def get_annotations(code_str):
    ''' String -> TypeCheckedResult(dict[str, dict[str, Type]], warnings list))
        Returns a TypeCheckedResult from a code string.
        If two type annotations refer to the same variable,
        the previous annotations is erased.
        '''
    codelines = code_str.split("\n")
    return get_annotations_from_ast(ast.parse(code_str), codelines)