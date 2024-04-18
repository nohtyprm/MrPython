import ast

# This class is made to update precondition nodes to match them with
# the right line
# Not updating could mismatch traceback lineno with the expected precondition line
class PreconditionAstLinenoUpdater(ast.NodeVisitor):

    def __init__(self, lineno):
        self.lineno = lineno

    def visit(self, node):
        if hasattr(node, 'lineno'):
            node.lineno = self.lineno
        if hasattr(node, 'end_lineno'):
            node.end_lineno = self.lineno
        self.generic_visit(node)