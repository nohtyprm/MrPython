
"""The abstract syntax tree of programs."""

import ast
import tokenize
import astpp

class Program:
    def __init__(self):
        # python parsed AST
        self.ast = None

        # list[str:Import]
        # the list of imported modules
        self.imports = dict()

        # dict[str:FunctionDef]
        # the list of function definitions in the program
        self.functions = dict()

        # test cases
        self.test_cases = []

        # other top level definitions
        self.other_top_defs = []

    def build_from_ast(self, modast):
        if not isinstance(modast, ast.Module):
            raise ValueError("Cannot build program from AST: not a module")
        self.ast = modast

        for node in modast.body:
            #print(node._attributes)
            if isinstance(node, ast.Import):
                imp_ast = Import(node)
                self.imports[imp_ast.name] = imp_ast
            elif isinstance(node, ast.FunctionDef):
                fun_ast = FunctionDef(node)
                if fun_ast.python101ready:
                    self.functions[fun_ast.name] = fun_ast
                else:
                    self.other_top_defs.append(UnsupportedNode(node))
            elif isinstance(node, ast.Assert):
                assert_ast = TestCase(node)
                self.test_cases.append(assert_ast)
            else:
                self.other_top_defs.append(UnsupportedNode(node))

class UnsupportedNode:
    def __int__(self, node):
        self.ast = node

class Import:
    def __init__(self, node):
        self.ast = node
        #print_ast_fields(self.ast)
        alias = self.ast.names[0]
        self.name = alias.name

class FunctionDef:
    def __init__(self, node):
        self.python101ready = False
        self.ast = node
        self.name = self.ast.name
        #print(astpp.dump(self.ast))

        self.parameters = []
        for arg_obj in self.ast.args.args:
            self.parameters.append(arg_obj.arg)

        first_instr = self.ast.body[0]
        next_instr_index = 0
        if isinstance(first_instr, ast.Expr) and isinstance(first_instr.value, ast.Str):
            self.docstring = first_instr.value.s
            next_instr_index = 1
            #print(self.docstring)

        self.body = []
        for inner_node in self.ast.body[next_instr_index:]:
            #print(astpp.dump(inner_node))
            self.body.append(parse_instruction(inner_node))

        self.python101ready = True


class TestCase:
    def __init__(self, node):
        self.ast = node




def parse_instruction(node):
    instruction_type_name = node.__class__.__name__
    #print("instruction type=",instruction_type_name)
    if instruction_type_name in INSTRUCTION_CLASSES:
        wrap_node = INSTRUCTION_CLASSES[instruction_type_name](node)
        return wrap_node
    else:
        return UnsupportedNode(node)


class Assign:
    def __init__(self, node):
        self.ast = node

class Return:
    def __init__(self, node):
        self.ast = node

INSTRUCTION_CLASSES = {"Assign" : Assign
                       , "Return" : Return}


def print_ast_fields(node):
    for field, val in ast.iter_fields(node):
        print(field)


def python_ast_from_file(filename):
    with tokenize.open(filename) as f:
        modtxt = f.read()
        modast = ast.parse(modtxt, mode="exec")
        return modast

if __name__ == "__main__":
    aire_ast = python_ast_from_file("../../examples/aire.py")
    #print(astpp.dump(aire_ast))

    prog1 = Program()
    prog1.build_from_ast(aire_ast)
    
