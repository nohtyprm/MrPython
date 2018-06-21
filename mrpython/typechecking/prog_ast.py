
"""The abstract syntax tree of programs."""

class Program:
    def __init__(self, ast):
        # python parsed AST
        self.ast = ast

        # list[Import]
        # the list of imported modules
        self.imports = []
        
        # list[FunctionDef]
        # the list of function definitions in the program
        self.function_defs = []

        # list[TestCase]
        # the list of test cases
        self.test_cases = []

        
        
