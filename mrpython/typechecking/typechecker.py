
from prog_ast import *
from type_ast import *
from type_parser import (type_expression_parser, function_type_parser)

class TypeError:
    def is_fatal(self):
        raise NotImplementedError("is_fatal is an abstract method")


class TypingContext:
    def __init__(self):
        self.type_errors = []
        self.global_env = {}
        self.functions = {}
        self.fatal_error = False

    def add_type_error(self, error):
        self.type_errors.append(error)
        if error.is_fatal():
            self.fatal_error = True

    def register_import(self, import_map):
        for (fname, ftype) in import_map.items():
            self.global_env[fname] = ftype

    def register_function(self, fun_name, signature, fun_def):
        self.functions[fun_name] = fun_def
        self.global_env[fun_name] = signature

    def __repr__(self):
        return "<TypingContext[genv={}, errors={}]>".format(self.global_env, self.type_errors)

# Takes a program, and returns a
# (possibly empty) list of type errors
def type_check_Program(prog):
    ctx = TypingContext() 

    # first step : fetch the imports
    # to fill the global environment
    for import_name in prog.imports:
        if import_name in REGISTERED_IMPORTS:
            ctx.register_import(REGISTERED_IMPORTS[import_name])
        else:
            ctx.add_type_error(UnsupportedImportError(import_name, prog.imports[import_name]))

    # second step : process each function to fill the global environment
    for (fun_name, fun_def) in prog.functions.items():
        #print("function: "+ fun_name)
        #print(fun_def.docstring)
        signature = function_type_parser(fun_def.docstring)
        #print(repr(signature))
        if signature.iserror:
            ctx.add_type_error(SignatureParseError(fun_name, fun_def))
        else:
            ctx.register_function(fun_name, signature.content, fun_def)

    # third step : type-check each function
    for (fun_name, fun_def) in ctx.functions.items():
        signature = ctx.global_env[fun_name]
        print("TODO type-checking: ", fun_name)

    return ctx

Program.type_check = type_check_Program


MATH_IMPORTS = {
    'math.sqrt' : function_type_parser("Number -> float").content
}

REGISTERED_IMPORTS = {
    'math' : MATH_IMPORTS
}


## All the possible kinds of error follow

class UnsupportedImportError(TypeError):
    def __init__(self, import_name, import_ast):
        self.import_name = import_name
        self.import_ast = import_ast

    def is_fatal(self):
        return False

if __name__ == '__main__':
    #print(repr(MATH_IMPORTS['math.sqrt']))

    aire_ast = python_ast_from_file("../../examples/aire.py")
    #print(astpp.dump(aire_ast))

    prog1 = Program()
    prog1.build_from_ast(aire_ast)

    ctx = prog1.type_check()
    print(repr(ctx))
