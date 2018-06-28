
from prog_ast import *
from type_ast import *

class TypeError:
    pass

class TypingContext:
    def __init__(self):
        self.type_errors = []

    def add_type_error(self, error):
        self.type_errors.append(error)

# Takes a program, and returns a
# (possibly empty) list of type errors
def type_check_Program(prog):
    ctx = TypingContext() 

    # first step : fech the imports
    # to fill the global environment
    for import_name in self.imports:
        if import_name in REGISTERED_IMPORTS:
            register_import(ctx, REGISTERED_IMPORTS[import_name])
        else:
            ctx.add_type_error(UnsupportedImportError(import_name, self.imports[import_name]))



REGISTERED_IMPORTS = {
    'math' : MATH_IMPORTS
}

MATH_IMPORTS = {
    'math.sqrt' : 
}

## All the possible kinds of error follow

class UnsupportedImportError(TypeError):
    def __init__(self, import_name, import_ast):
        self.import_name = import_name
        self.import_ast = import_ast

if __name__ == '__main__':
    pass
