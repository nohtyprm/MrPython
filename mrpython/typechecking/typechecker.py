import os.path, sys

if __name__ == "__main__":
    main_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    found_path = False
    for path in sys.path:
        if path == main_path:
            found_path = True
            break
    if not found_path:
        sys.path.append(main_path)

    from prog_ast import *
    from type_ast import *
    from type_parser import (type_expression_parser, function_type_parser)

    from translate import tr
else:

    from .prog_ast import *
    from .type_ast import *
    from .type_parser import (type_expression_parser, function_type_parser)

    from ..translate import tr

class TypeError:
    def is_fatal(self):
        raise NotImplementedError("is_fatal is an abstract method")


class TypingContext:
    def __init__(self, prog):
        self.prog = prog
        self.type_errors = []
        self.global_env = {}
        self.functions = {}
        self.fatal_error = False
        self.param_env = None
        self.return_type = None
        self.function_def = None
        self.partial_function = None
        self.allow_declarations = None
        self.parent_stack = None
        self.local_env = None

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

    def register_parameters(self, parameters, param_types):
        self.param_env = {}
        for (param, param_type) in zip(parameters, param_types):
            self.param_env[param] = param_type

    def register_return_type(self, return_type):
        self.return_type = return_type

    def register_function_def(self, func_def, partial):
        self.function_def = func_def
        self.partial_function = partial
        # are variable declarations allowed ?
        self.allow_declarations = True
        # for nested construction (while, for, if ...)
        self.parent_stack = []
        # remark: local (lexical) environment disallow shadowing
        self.local_env = {}

    def fetch_nominal_type(self, base_type):
        # TODO : follow metavar instantiations
        # (for now, just return the type as it is)
        return base_type

    def unregister_function_def(self):
        self.param_env = None
        self.return_type = None
        self.function_def = None
        self.partial_function = None
        self.parent_stack = None
        self.allow_declarations = None
        self.local_env = None

    def fetch_scope_mode(self):
        # TODO : complete with parent stack
        if not self.parent_stack:
            return 'function'

    def __repr__(self):
        return "<TypingContext[genv={}, errors={}]>".format(self.global_env, self.type_errors)

#############################################
# Type checking                             #
#############################################

# Takes a program, and returns a
# (possibly empty) list of type errors
def type_check_Program(prog):
    ctx = TypingContext(prog) 

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
            ctx.add_type_error(SignatureParseError(fun_name, fun_def, signature))
        else:
            ctx.register_function(fun_name, signature.content, fun_def)

    # third step : type-check each function
    for (fun_name, fun_def) in ctx.functions.items():
        fun_def.type_check(ctx)
        if ctx.fatal_error:
            return ctx

    return ctx

Program.type_check = type_check_Program

def type_check_FunctionDef(func_def, ctx):
    signature = ctx.global_env[func_def.name]
    #print("signature = ", repr(signature))

    # Step 1: check function arity
    if len(func_def.parameters) != len(signature.param_types):
        ctx.add_type_error(FunctionArityError(func_def, signature))
        # this is of course a fatal error
        return

    # Step 2 : fill the parameter environment, and expected return type
    ctx.register_parameters(func_def.parameters, signature.param_types)
    #print(ctx.param_env)
    ctx.register_return_type(signature.ret_type)
    ctx.register_function_def(func_def, signature.partial)

    # Step 3 : type-check body
    for instr in func_def.body:
        if isinstance(instr, UnsupportedNode):
            ctx.add_type_error(UnsupportedNodeError(func_def, instr))
            # we abort the type-checking of this function
            ctx.unregister_function_def()
            return

        #print(repr(instr))
        instr.type_check(ctx)
        if ctx.fatal_error:
            ctx.unregister_function_def()
            return

FunctionDef.type_check = type_check_FunctionDef

def type_check_Assign(assign, ctx):
    # Step 1: distinguish between initialization and proper assignment
    if assign.var_name not in ctx.local_env:
        # initialization
        # Step 2a) check if declaration is allowed here
        if not ctx.allow_declarations:
            ctx.add_type_error(DisallowedDeclaration(ctx.function_def, assign))
            return
        # Step 3a) fetch declared type
        declared_type = fetch_declaration_type(ctx, assign)
        if declared_type is None:
            return
        # Step 4a) infer type of initialization expression
        expr_type = assign.expr.type_infer(ctx)
        if not expr_type:
            return
        # Step 5a) compare inferred type wrt. declared type
        if not expr_type.type_compare(ctx, declared_type):
            return
        # Step 6a) register declared type in environment
        ctx.local_env[assign.var_name] = (declared_type, ctx.fetch_scope_mode())

    else: # proper assignment
        raise NotImplementedError("Proper assignment not yet implemented")

def fetch_declaration_type(ctx, assign):
    lineno = assign.ast.lineno
    decl_line = ctx.prog.get_source_line(lineno-1).strip()

    #print(decl_line)
    if (not decl_line) or decl_line[0] != '#':
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, tr("Missing '#' character in variable declaration")))
        return None
    decl_line = decl_line[1:].strip()
    if (not decl_line) or decl_line[0] != assign.var_name:
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, tr("Missing variable name '{}' in declaration").format(assign.var_name)))
        return None
    decl_line = decl_line[1:].strip()
    if (not decl_line) or decl_line[0] != ':':
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, tr("Missing ':' character before variable type declaration")))
        return None
    decl_line = decl_line[1:].strip()
    decl_type = type_expression_parser(decl_line)
    if decl_type.iserror:
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, tr("Don't understand the declared type: {}").format(decl_type)))
        return None
    #print(decl_type.content)
    return decl_type.content

Assign.type_check = type_check_Assign

def type_check_Return(ret, ctx):
    # Compare with expected return type
    expr_type = type_expect(ctx, ret.expr, ctx.return_type)
    if expr_type is None:
        ctx.add_type_error(WrongReturnTypeError(ctx.function_def, ret, ctx.return_type, ctx.partial_function))
        return
    # no error here
    return

Return.type_check = type_check_Return

######################################
# Type inference                     #
######################################

def infer_number_type(ctx, type1, type2):
    # number always "wins"
    if isinstance(type1, NumberType):
        return type1
    if isinstance(type2, NumberType):
        return type2
    # otherwise it's float
    if isinstance(type1, FloatType):
        return type1
    if isinstance(type2, FloatType):
        return type2

    # otherwise it's either of the two
    return type1


# The rule for EAdd:
#
#      e1 :: Number[x]   e2 :: Number[x]
#      ---------------------------------
#      e1 + e2  ::>  x

def type_infer_EAdd(expr, ctx):
    left_type = type_expect(ctx, expr.left, NumberType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, NumberType())
    if not right_type:
        return None

    add_type = infer_number_type(ctx, left_type, right_type)
    if not add_type:
        return None

    return add_type

EAdd.type_infer = type_infer_EAdd

def type_infer_ESub(expr, ctx):
    left_type = type_expect(ctx, expr.left, NumberType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, NumberType())
    if not right_type:
        return None

    sub_type = infer_number_type(ctx, left_type, right_type)
    if not sub_type:
        return None

    return sub_type

ESub.type_infer = type_infer_ESub

def type_infer_EMult(expr, ctx):
    left_type = type_expect(ctx, expr.left, NumberType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, NumberType())
    if not right_type:
        return None

    mult_type = infer_number_type(ctx, left_type, right_type)
    if not mult_type:
        return None

    return mult_type

EMult.type_infer = type_infer_EMult

# The rule for EDiv:
#
#      e1 :: Number   e2 :: Number
#      ---------------------------
#      e1 / e2  ::>  float

def type_infer_EDiv(expr, ctx):
    left_type = type_expect(ctx, expr.left, NumberType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, NumberType())
    if not right_type:
        return None

    return FloatType()

EDiv.type_infer = type_infer_EDiv

def type_infer_EVar(var, ctx):
    # check if the var is a parameter
    if var.name in ctx.param_env:
        return ctx.param_env[var.name]
    # or else lookup in the local environment
    if var.name in ctx.local_env:
        var_type, _ = ctx.local_env[var.name]
        return var_type
    # or the variable is unknown
    ctx.add_type_error(UnknownVariableError(ctx.function_def, var))
    return None

EVar.type_infer = type_infer_EVar

def type_infer_ENum(num, ctx):
    if isinstance(num.value, int):
        return IntType()
    if isinstance(num.value, float):
        return FloatType()

    # or it's an unsupported numeric type
    ctx.add_type_error(UnsupportedNumericTypeError(ctx.function_def, num))
    return None

ENum.type_infer = type_infer_ENum

def type_infer_ECall(call, ctx):
    # step 1 : fetch the signature of the called function
    if not call.fun_name in ctx.global_env:
        ctx.add_type_error(UnknownFunctionError(ctx.function_def, call))
        return None

    signature = ctx.global_env[call.fun_name]
    #print(repr(signature))

    # step 2 : check the call arity
    if len(signature.param_types) != len(call.arguments):
        ctx.add_type_error(CallArityError(ctx.function_def, signature, call))
        return None

    # step 3 : check the argument types
    for (num_arg, arg, param_type) in zip(range(1), call.arguments, signature.param_types):
        arg_type = type_expect(ctx, arg, param_type)
        if arg_type is None:
            ctx.add_type_error(CallArgumentError(ctx.function_def, call, num_arg, arg, param_type))
            return

    # step 4 : return the return type
    return signature.ret_type

ECall.type_infer = type_infer_ECall


######################################
# Type comparisons                   #
######################################

def type_expect(ctx, expr, expected_type):
    expr_type = expr.type_infer(ctx)
    if not expr_type:
        return None
    if not expected_type.type_compare(ctx, expr_type):
        return None
    return expr_type

def type_compare_NumberType(expected_type, ctx, expr_type):
    if isinstance(expr_type, NumberType) \
       or isinstance(expr_type, IntType) \
       or isinstance(expr_type, FloatType): 
        return True

    ctx.add_type_error(TypeComparisonError(ctx.function_def, expr_type, tr("Expecting a Number")))
    return False

NumberType.type_compare = type_compare_NumberType

def type_compare_IntType(expected_type, ctx, expr_type):
    if isinstance(expr_type, IntType):
        return True

    ctx.add_type_error(TypeComparisonError(ctx.function_def, expr_type, tr("Expecting an int")))
    return False

IntType.type_compare = type_compare_IntType

def type_compare_FloatType(expected_type, ctx, expr_type):
    if isinstance(expr_type, FloatType):
        return True

    ctx.add_type_error(TypeComparisonError(ctx.function_def, expr_type, tr("Expecting a float")))
    return False

FloatType.type_compare = type_compare_FloatType

######################################
# Standard imports                   #
######################################


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

    def fail_string(self):
        return "UnsupportedImportError[{}]@{}:{}".format(self.import_name, self.import_ast.ast.lineno, self.import_ast.ast.col_offset)

    def is_fatal(self):
        return False

class SignatureParseError(TypeError):
    def __init__(self, fun_name, fun_def, signature):
        self.fun_name = fun_name
        self.fun_def = fun_def
        self.signature = signature

    def fail_string(self):
        return "SignatureParseError[{}]@{}:{}".format(self.fun_name, self.fun_def.ast.lineno, self.fun_def.ast.col_offset)

    def is_fatal(self):
        return False


class FunctionArityError(TypeError):
    def __init__(self, func_def, signature):
        self.func_def = func_def
        self.signature = signature

    def is_fatal(self):
        return True

class UnsupportedNodeError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node

    def is_fatal(self):
        return True

class DisallowedDeclarationError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node

    def is_fatal(self):
        return True

class DeclarationError(TypeError):
    def __init__(self, in_function, node, explain):
        self.in_function = in_function
        self.node = node
        self.explain = explain

    def is_fatal(self):
        return True

class UnknownVariableError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node

    def is_fatal(self):
        return True

class TypeComparisonError(TypeError):
    def __init__(self, in_function, typ, explain):
        self.in_function = in_function
        self.type = typ

    def is_fatal(self):
        return True

class UnsupportedNumericTypeError(TypeError):
    def __init__(self, in_function, num):
        self.in_function = in_function
        self.num = num

    def is_fatal(self):
        return True

class WrongReturnTypeError(TypeError):
    def __init__(self, in_function, ret, ret_type, partial_function):
        self.in_function = in_function
        self.ret = ret
        self.ret_type = ret_type
        self.partial_function = partial_function

    def is_fatal(self):
        return True

class UnknownFunctionError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node

    def is_fatal(self):
        return True

class CallArityError(TypeError):
    def __init__(self, in_function, signature, call):
        self.in_function = in_function
        self.signature = signature
        self.call = call

    def is_fatal(self):
        return True

class CallArgumentError(TypeError):
    def __init__(self, in_function, call, num_arg, arg, param_type):
        self.in_function = in_function
        self.call = call
        self.num_arg = num_arg
        self.arg = arg
        self.param_type = param_type

    def is_fatal(self):
        return True


if __name__ == '__main__':

    prog1 = Program()
    prog1.build_from_file("../../examples/aire.py")

    ctx = prog1.type_check()
    print(repr(ctx))
