import ast
import astor
import pdb
from mrpython.typechecking.typer import TypeEnum


class TypingError(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class TypeChecker(ast.NodeVisitor):
    def __init__(self):
        self.return_type = None
        # FIXME: Make the environment a class member

    # Check functions
    def check_bool(self, node):
        print("Checking...")
        if self.return_type != TypeEnum.BOOL:
                raise TypingError(astor.to_source(node),
                             "Expected type bool, got " + str(self.return_type))
    
    # Visitor functions
    def visit_NameConstant(self, node):
        if node.value == True or node.value == False:
            self.return_type = TypeEnum.BOOL
        else:
            self.return_type = None

    def visit_and(self, node):
        left = node.values[0]
        right = node.values[1]
        self.visit(left)
        self.check_bool(node)
        self.visit(right)
        self.check_bool(node)
        self.return_type = TypeEnum.BOOL

    def visit_not(self, node):
        self.visit(node.values[0])
        self.check_bool(node)
        self.return_type = TypeEnum.BOOL

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            self.visit_and(node)
        if isinstance(node.op, ast.Not):
            self.visit_not(node)

    def generic_visit(self, node):
        super().generic_visit(node)

node = ast.parse("True and None")
chk = TypeChecker()
chk.visit(node)
