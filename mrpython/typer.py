import ast
from type_annotation_parser import TypeAnnotationParser

class AssignAggregator(ast.NodeVisitor):
    def __init__(self):
        self.assigns = []

    def visit_Assign(self, node):
        self.assigns.append(node)

def get_annotations(filename):
    file = open(filename)
    # Build a list of all lines for easy access to specific line
    code = file.readlines()
    # Get back to start of file for ast parsing
    file.seek(0)
    walker = AssignAggregator()
    walker.visit(ast.parse(file.read()))
    type_annotation_lines = [code[node.lineno - 2] for node in walker.assigns]
    return type_annotation_lines

def build_type_dict(type_annotation_lines):
    ''' Use a popparser to parse type annotations'''
    type_dict = {}
    parser = TypeAnnotationParser()
    parse_results = [parser.parse_from_string(code)\
                        for code in type_annotation_lines]

    for result in parse_results:
        # Note that we reject every ill-formed annotation in the
        # process of removing non-annotation lines.
        if not result.iserror:
            type_dict[result.content.id] = result.content.type
    return type_dict
