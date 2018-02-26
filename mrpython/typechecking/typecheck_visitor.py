import ast
import astor
import pdb
from mrpython.typechecking.typer import TypeEnum


class TypeMismatchError(Exception):
    def __init__(self, node, expect_ty, ret_type):
        self.msg = "Error in " + astor.to_source(node) +\
                   "Expected type " + repr(expect_ty) + ", got " + repr(ret_type)

class VarNotInScopeError(Exception):
    def __init__(self, node, var_id):
        self.msg = "Error: Variable " + var_id + " not in scope line " + node.lineno

class FuncNotInScopeError(Exception):
    def __init__(self, node, func_id):
        self.msg = "Error: Function " + func_id + " is not in scope."

class TypeChecker(ast.NodeVisitor):
    def __init__(self, func_env={}, var_env={}):
        self.return_type = None
        self.var_env = var_env
        self.func_env = func_env
        # Since we don't want to stop typechecking on an error
        self.warnings = []

    # Check functions
    def check_ty(self, node, ret_ty):
        if self.return_type != ret_ty:
            self.warnings.append(TypeMismatchError(node, ret_ty, self.return_type))

    def check_bool(self, node):
        self.check_ty(node, TypeEnum.BOOL)
    
    # Visitor functions
    def visit_Call(self, node):
        if node.func.id in self.func_env:
            func_ty = self.func_env[node.func.id]
            params = func_ty.params
            for param_ty, arg in params, node.args:
                self.visit(arg)
                self.check_ty(arg, param_ty)
            self.return_type = func_ty.ret_ty
        else:
            warn = FuncNotInScopeError(node, node.func.id)
            self.warnings.append(warn)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.name in self.var_env:
                self.last_type = self.var_env[node.name]
            else:
                self.warnings.append(VarNotInScopeError(node, node.name))

    def visit_NameConstant(self, node):
        if node.value == True or node.value == False:
            self.return_type = TypeEnum.BOOL
        else:
            self.return_type = None

    def visit_BoolOp(self, node):
        # a or b or c is collapsed into a single Or node
        for operand in node.values:
            self.visit(operand)
            self.check_bool(operand)
        self.return_type = TypeEnum.BOOL

    # We implement this for debugging purposes
    def generic_visit(self, node):
        super().generic_visit(node)
        return self

node = ast.parse("True and None")
chk = TypeChecker()
chk.visit(node)
