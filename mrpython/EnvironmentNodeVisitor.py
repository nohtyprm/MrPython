from ast import NodeVisitor

class EnvironmentNodeVisitor(NodeVisitor):
    """
    Inherits NodeVisitor override generic_visit : all the function and variable
    names are added to the name_list
    Give other information : line of the functions
    """

    def __init__(self):
        self.name_list = set()
        self.function_lines = set()

    def visit_Name(self, node):
        """ For adding the variable names in the name_list """
        self.name_list.add(node.id)

    def visit_FunctionDef(self, node):
        """ For adding the name of the defined functions """
        self.name_list.add(node.name)
        self.function_lines.add((node.name, node.lineno))
