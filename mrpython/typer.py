import ast
from type_annotation_parser import TypeAnnotationParser

class AssignAggregator(ast.NodeVisitor):
    def __init__(self):
        self.assigns = []

    def visit_Assign(self, node):
        self.assigns.append(node)

class Type():
    def __init__(self, kind, lineno=None):
        self.kind = kind
        # Useful for parse information
        self.lineno = lineno

    def __repr__(self):
        res = "Type(\"" + self.kind + "\""
        if self.lineno:
            res += ", " + str(self.lineno)
        return res + ")"

# FIXME: When we'll call this functions, we'll probably have an offset problem
def get_annotations_from_ast(tree, codelines):
    ''' ast -> string list -> Type dict)
        Returns a dictionary of type information from an
        ast and a list of lines of code. The latter is needed
        in order to get back the annotation.
    '''
    type_dict = {}
    walker = AssignAggregator()
    parser = TypeAnnotationParser()
    walker.visit(tree)

    for assign in walker.assigns:
        parse_result = parser.parse_from_string(codelines[assign.lineno - 2])
        if not parse_result.iserror:
            var_type = Type(parse_result.content.type, assign.lineno)
            type_dict[parse_result.content.name] = var_type

    return type_dict

def get_annotations(code_str):
    ''' String -> Type Dict '''
    codelines = code_str.readlines()
    return get_annotations_from_ast(ast.parse(code_str), codelines)