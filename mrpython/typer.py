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

def get_annotations(filename):
    ''' string -> (id -> Type)
        Returns a dictionary of type information from a
        file name.
    '''
    type_dict = {}
    file = open(filename)
    # Build a list of all lines for easy access to specific line
    code = file.readlines()
    # Get back to start of file for ast parsing
    file.seek(0)

    walker = AssignAggregator()
    parser = TypeAnnotationParser()
    walker.visit(ast.parse(file.read()))
    for assign in walker.assigns:
        parse_result = parser.parse_from_string(code[assign.lineno - 2])
        if not parse_result.iserror:
            var_type = Type(parse_result.content.type, assign.lineno)
            type_dict[parse_result.content.name] = var_type
    return type_dict
