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
    from type_parser import (type_expression_parser, function_type_parser, type_def_parser)

    from translate import tr
else:
    from .prog_ast import *
    from .type_ast import *
    from .type_parser import (type_expression_parser, function_type_parser, type_def_parser)

    from .translate import tr

class TypeError:
    def is_fatal(self):
        raise NotImplementedError("is_fatal is an abstract method")


class TypingContext:
    def __init__(self, prog):
        self.prog = prog
        self.type_errors = []
        self.type_defs = {}
        self.global_env = {}
        self.functions = {}
        self.fatal_error = False
        self.param_env = None
        self.return_type = None
        self.function_def = None
        self.partial_function = None
        self.dead_variables = set()
        self.parent_stack = None
        self.local_env = None
        self.call_type_env = [] # stack of type environments when calling generic functions
        self.local_env = {}  # will have global variables

    def add_type_error(self, error):
        self.type_errors.append(error)
        if error.is_fatal():
            self.fatal_error = True

    def has_error(self):
        return len(self.type_errors) > 0

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
        # for nested construction (while, for, if ...)
        self.parent_stack = []
        # remark: local (lexical) environment disallow shadowing
        self.save_local_env = self.local_env.copy()
        self.save_dead_variables = self.dead_variables.copy()

    def push_parent(self, parent_node):
        parent_local_env = { var_name : var_info for (var_name, var_info) in self.local_env.items() }
        self.parent_stack.append((parent_node, parent_local_env))

    def pop_parent(self):
        if not self.parent_stack:
            raise ValueError("Cannot pop from empty parent stack (please report)")

        # all variables defined within the parent are now disallowed
        _, parent_local_env = self.parent_stack.pop()
        for var in self.local_env:
            if var not in parent_local_env:
                self.dead_variables.add(var)

        self.local_env = parent_local_env

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
        self.local_env = self.save_local_env
        self.save_local_env = None
        self.dead_variables = self.save_dead_variables
        self.save_dead_variables = None

    def fetch_scope_mode(self):
        # TODO : complete with parent stack
        if not self.parent_stack:
            return 'function'

    def __repr__(self):
        return "<TypingContext[genv={}, errors={}]>".format(self.global_env, self.type_errors)

#############################################
# Type checking                             #
#############################################

def type_check_UnsupportedNode(node, ctx):
    print("Error: Type checking not supported for this node")
    import astpp
    print(astpp.dump(node.ast))
    ctx.add_type_error(UnsupportedNodeError(None, node))

    return ctx

UnsupportedNode.type_check = type_check_UnsupportedNode

# Takes a program, and returns a
# (possibly empty) list of type errors
def type_check_Program(prog):
    ctx = TypingContext(prog) 

    # first step : parse all type definitions
    if prog.source_lines is None: # Hackish ...
        prog.source_lines = prog.source.split('\n')

    for i in range(len(prog.source_lines)):
        source_line = prog.source_lines[i]
        type_name, parse_result = type_def_parser(source_line)
        if type_name is not None:
            if parse_result.iserror:
                ctx.add_type_error(TypeDefParseError(i+1, type_name))
            elif type_name in ctx.type_defs:
                ctx.add_type_error(DuplicateTypeDefError(i+1, type_name))
            else:
                type_def = parse_result.content.unalias(ctx.type_defs)
                ctx.type_defs[type_name] = type_def

    # second step :  fill the global environment

    # first register the builtins
    ctx.register_import(REGISTERED_IMPORTS[''])

    # then register the imports
    for import_name in prog.imports:
        if import_name in REGISTERED_IMPORTS:
            ctx.register_import(REGISTERED_IMPORTS[import_name])
        else:
            ctx.add_type_error(UnsupportedImportError(import_name, prog.imports[import_name]))

    # third step : process each function to fill the global environment
    for (fun_name, fun_def) in prog.functions.items():
        #print("function: "+ fun_name)
        #print(fun_def.docstring)
        signature = function_type_parser(fun_def.docstring)
        #print(repr(signature))
        if signature.iserror:
            ctx.add_type_error(SignatureParseError(fun_name, fun_def, signature))
        else:
            fun_type = signature.content.unalias(ctx.type_defs)
            ctx.register_function(fun_name, fun_type, fun_def)

    # fourth step : type-check each function
    for (fun_name, fun_def) in ctx.functions.items():
        fun_def.type_check(ctx)
        if ctx.fatal_error:
            return ctx

    # fifth step: process each global variable definitions
    # (should not be usable from functions so it comes after)
    for global_var in prog.global_vars:
        global_var.type_check(ctx)
        if ctx.fatal_error:
            return ctx

    # sixth step: type-check test assertions
    for test_case in prog.test_cases:
        test_case.type_check(ctx)
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
        if ctx.has_error():
            ctx.unregister_function_def()
            return

    ctx.unregister_function_def()

FunctionDef.type_check = type_check_FunctionDef

def parse_var_name(declaration):
    vdecl = ""
    expect_colon = False
    for i in range(0, len(declaration)):
        if declaration[i] == ':' and expect_colon:
            return (vdecl, declaration[i:])
        elif not declaration[i].isspace():
            if expect_colon:
                return vdecl, declaration[i-1:]
            vdecl += declaration[i]
        else:
            if vdecl != "":
                expect_colon = True

    return None, None

def parse_declaration_type(ctx, lineno):
    """parse a declared type: returns a pair (v, T) with v the declared
variable name and T its type, or (None, msg, err_cat) with an informational message if the parsing fails."""
    
    decl_line = ctx.prog.get_source_line(lineno).strip()
    
    if (not decl_line) or decl_line[0] != '#':
        return (None, tr("Missing variable declaration"), 'header-char')
    
    decl_line = decl_line[1:].strip()
    var_name, decl_line = parse_var_name(decl_line)

    #print(var_name)
    if (not decl_line) or decl_line[0] != ':':
        return (None, tr("Missing ':' character before variable type declaration"), 'colon')

    decl_line = decl_line[1:].strip()
    decl_type = type_expression_parser(decl_line)
    #print("rest='{}'".format(decl_line[decl_type.end_pos.offset:]))
    if decl_type.iserror: # or decl_line[decl_type.end_pos.offset:]!='': (TODO some sanity check ?)
        return (None, tr("I don't understand the declared type for variable '{}'").format(var_name), 'parse')

    remaining = decl_line[decl_type.end_pos.offset:].strip()
    if remaining != '' and not remaining.startswith('('):
        return (None, tr("The declared type for variable '{}' has strange appended string: {}").format(var_name, remaining), 'parse')
        
    return (var_name, decl_type.content, "")

def fetch_assign_declaration_types(ctx, assign_target, strict=False):
    lineno = assign_target.ast.lineno - 1

    # the required variables (except underscore)
    req_vars = { v.var_name for v in assign_target.variables() if v.var_name != "_" }
    if not req_vars:  # if there is no required var, this means all vars are _'s
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("The special variable '_' cannot be use alone")))
        return None
    
    declared_types = dict()

    for _ in assign_target.variables():

        var_name, decl_type, err_cat = parse_declaration_type(ctx, lineno)
        if var_name is None:
            if strict: # in strict mode we require the declaration (only for mono-vars, for now)
                ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, err_cat, assign_target.ast.lineno if err_cat=='header-char' else lineno, decl_type))
                return None

            return declared_types

        if var_name in declared_types:
            ctx.add_type_error(DuplicateMultiAssign(var, assign_target))
            return None

        if var_name == "_":
            ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("The special variable '_' cannot be declared")))
            return None

        if var_name not in req_vars: # if not a special var, it must be required
            ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("Unused variable name '{}' in declaration").format(var_name)))
        
        else:
            req_vars.remove(var_name)
            declared_types[var_name] = decl_type.unalias(ctx.type_defs)

        lineno -= 1

    if strict and req_vars: # need all declarations in strict mode
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'unknown-vars', assign_target.ast.lineno, tr("Variables not declared: {}").format((v.var_name for f in req_vars))))
        return None

    return declared_types

def linearize_tuple_type(tuple_type):
    if not isinstance(tuple_type, TupleType):
        raise NotSupportedError("Can only linearize tuple types (please report)")

    elem_types = []

    for elem_type in tuple_type.elem_types:
        if isinstance(elem_type, TupleType):
            elem_types.extend(linearize_tuple_type(elem_type))
        else:
            elem_types.append(elem_type)

    return elem_types
    
def type_check_Assign(assign, ctx):
    
    # first let's see if the variables are dead
    mono_assign = False # is this an actual assignment (and not an initialization ?)
    for var in assign.target.variables():
        if var.var_name in ctx.dead_variables:
            ctx.add_type_error(DeadVariableUseError(var.var_name, var))
            return False

        if var.var_name in ctx.local_env:
            if assign.target.arity() > 1:
                # Multiple assigment is forbidden (only multi-declaration allowed)
                ctx.add_type_error(ForbiddenMultiAssign(var.var_name, var))
                return False
            else:
                mono_assign = True

    if mono_assign:
        expr_type = assign.expr.type_infer(ctx)
        if expr_type is None:
            return False

        # nothing else to do for actual assignment
        return True

    # here we consider an initialization and not an actual assignment
    
    # next fetch the declared types  (only required for mono-variables)

    declared_types = fetch_assign_declaration_types(ctx, assign.target, True if assign.target.arity() == 1 else False)
    if declared_types is None:
        declared_types = dict()

    # next infer type of initialization expression
    expr_type = assign.expr.type_infer(ctx)
    if expr_type is None:
        return False
    
    # treat the simpler "mono-var" case first
    if assign.target.arity() == 1:
        var = assign.target.variables()[0]
        if var.var_name not in declared_types:
            # XXX: this is strict, need a dedicated error message ?
            return False
        
        # compare inferred type wrt. declared type
        if not declared_types[var.var_name].type_compare(ctx, assign.expr, expr_type):
            return False

        # register declared type in environment
        ctx.local_env[var.var_name] = (declared_types[var.var_name], ctx.fetch_scope_mode())

        return True
        
    # here we have a destructured initialization

    
    if not isinstance(expr_type, TupleType):
        ctx.add_type_error(TypeComparisonError(ctx.function_def, TupleType(), expr, expr_type,
                                               tr("Expecting a tuple")))
        return False

    expr_var_types = linearize_tuple_type(expr_type)

    if len(expr_var_types) != len(assign.target.variables()):
        ctx.add_type_error(TupleDestructArityError(assign, expr_type, len(expr_var_types), len(assign.target.variables())))
        return False

    for (i, var) in zip(range(0, len(assign.target.variables())), assign.target.variables()):
        if var.var_name == '_': # just skip this check
            continue

        if var.var_name in declared_types:
            if not declared_types[var.var_name].type_compare(ctx, assign.target, expr_var_types[i], raise_error=False):
                ctx.add_type_error(VariableTypeError(assign.target, var, declared_types[var_name], expr_var_types[i]))
                return False
        
            ctx.local_env[var.var_name] = (declared_types[var.var_name], ctx.fetch_scope_mode())
        else:
            ctx.local_env[var.var_name] = (expr_var_types[i], ctx.fetch_scope_mode())    

    return True

Assign.type_check = type_check_Assign

def type_check_For(for_node, ctx):

    # first let's see if the iter variables are dead or in the local environment
    for var in for_node.target.variables():
        if var.var_name in ctx.dead_variables:
            ctx.add_type_error(DeadVariableUseError(var.var_name, var))
            return False

        if var.var_name in ctx.local_env:
            ctx.add_type_error(IterVariableInEnvError(var.var_name, var))
            return False

    declared_types = fetch_assign_declaration_types(ctx, for_node.target, True if for_node.target.arity() == 1 else False)
    if declared_types is None:
        if for_node.target.arity() == 1:
            return False
        else:
            declared_types = dict()

    #print("declared_types={}".format(declared_types))
            
    # next infer type of initialization expression
    iter_type = for_node.iter.type_infer(ctx)
    if iter_type is None:
        return False

    #print("iter_type={}".format(iter_type))
    
    if isinstance(iter_type, IterableType) \
       or isinstance(iter_type, SequenceType) \
       or isinstance(iter_type, ListType) \
       or isinstance(iter_type, SetType) \
       or isinstance(iter_type, StrType):

        ctx.push_parent(for_node)

        # === do like in Assign ===

        # treat the simpler "mono-var" case first
        if for_node.target.arity() == 1:
            var = for_node.target.variables()[0]
            if var.var_name not in declared_types:
                # XXX: this is strict, need a dedicated error message ?
                ctx.pop_parent()
                return False
        
            # compare inferred type wrt. declared type
            if not declared_types[var.var_name].type_compare(ctx, for_node.iter, iter_type.elem_type if not isinstance(iter_type, StrType) else StrType()):
                ctx.pop_parent()
                return False

            # register declared type in environment
            ctx.local_env[var.var_name] = (declared_types[var.var_name], ctx.fetch_scope_mode())

        else:
            # here we have a destructured initialization
            expr_type = iter_type.elem_type if not isinstance(iter_type, StrType) else StrType()
            
            if not isinstance(expr_type, TupleType):
                ctx.add_type_error(TypeComparisonError(ctx.function_def, TupleType(), for_node.iter, expr_type,
                                                       tr("Expecting an iterator of tuples")))
                ctx.pop_parent()
                return False

            expr_var_types = linearize_tuple_type(expr_type)

            if len(expr_var_types) != len(for_node.target.variables()):
                ctx.add_type_error(TupleDestructArityError(for_node.target, expr_type, len(expr_var_types), len(for_node.target.variables())))
                ctx.pop_parent()
                return False

            for (i, var) in zip(range(0, len(for_node.target.variables())), for_node.target.variables()):
                if var.var_name == '_': # just skip this check
                    continue

                if var.var_name in declared_types:
                    if not declared_types[var.var_name].type_compare(ctx, var, expr_var_types[i], raise_error=False):
                        ctx.add_type_error(VariableTypeError(for_node.target, var, declared_types[var_name], expr_var_types[i]))
                        ctx.pop_parent()
                        return False
        
                    ctx.local_env[var.var_name] = (declared_types[var.var_name], ctx.fetch_scope_mode())
                else:
                    ctx.local_env[var.var_name] = (expr_var_types[i], ctx.fetch_scope_mode())    

        # and now type check the body in the constructed local env

        for instr in for_node.body:
            if not instr.type_check(ctx):
                ctx.pop_parent()
                return False

        ctx.pop_parent()
        return True
    
    # dictionary
    elif isinstance(iter_type, DictType):
        raise NotImplementedError("Dictionary type not yet supported")
    else: # unsupported iterator type
        ctx.add_type_error(IteratorTypeError(for_node, iter_type))
        return False

For.type_check = type_check_For


def fetch_iter_declaration_type(ctx, iter_node):
    lineno = iter_node.ast.lineno - 1

    var_name, decl_type, err_cat = parse_declaration_type(ctx, lineno)
    if var_name is None:
        # no error for iterator variables
        return None

    if var_name != iter_node.var_name:
        ctx.add_type_error(DeclarationError(ctx.function_def, iter_node, 'var-name', lineno, tr("Wrong variable name in declaration, it should be '{}'").format(iter_node.var_name)))
        return None
    
    return decl_type.unalias(ctx.type_defs)


def type_check_Return(ret, ctx):
    expr_type = ret.expr.type_infer(ctx)
    if not expr_type:
        return False
    if not ctx.return_type.type_compare(ctx, ret.expr, expr_type):
        ctx.add_type_error(WrongReturnTypeError(ctx.function_def, ret, ctx.return_type, ctx.partial_function))
        return False

    return True

Return.type_check = type_check_Return

def type_check_TestCase(assertion, ctx):
    expr_type = type_expect(ctx, assertion.expr, BoolType())
    if expr_type is None:
        return False
    return True

TestCase.type_check = type_check_TestCase

def type_check_If(ifnode, ctx):
    # push the parent for the scoping rule
    ctx.push_parent(ifnode)

    # 1. check condition is a boolean
    cond_type = type_expect(ctx, ifnode.cond, BoolType())
    if cond_type is None:
        ctx.pop_parent()
        return False

    # 2. check type of body
    for instr in ifnode.body:
        if not instr.type_check(ctx):
            ctx.pop_parent()
            return False

    # pop the parent and repush
    ctx.pop_parent()
    ctx.push_parent(ifnode)

    # 3. check type of orelse block
    for instr in ifnode.orelse:
        if not instr.type_check(ctx):
            ctx.pop_parent()
            return False

    ctx.pop_parent()
    return True

If.type_check = type_check_If

def type_check_While(wnode, ctx):
    # push the parent for the scoping rule
    ctx.push_parent(wnode)

    # 1. check condition is a boolean
    cond_type = type_expect(ctx, wnode.cond, BoolType())
    if cond_type is None:
        ctx.pop_parent()
        return False

    # 2. check type of body
    for instr in wnode.body:
        if not instr.type_check(ctx):
            ctx.pop_parent()
            return False

    # pop the parent and repush
    ctx.pop_parent()

    return True

While.type_check = type_check_While

def type_check_ECall(enode, ctx):
    call_type = enode.type_infer(ctx)
    if call_type is None:
        return False
    elif isinstance(call_type, NoneTypeType):
        return True
    else: # the return type is not None: it's a warning
        ctx.add_type_error(CallNotNoneError(enode, call_type))

ECall.type_check = type_check_ECall

######################################
# Type inference                     #
######################################

def type_infer_UnsupportedNode(node, ctx):
    print("Error: Type inference for unsupported node")
    import astpp
    print(astpp.dump(node.ast))
    ctx.add_type_error(UnsupportedNodeError(None, node))

    return False


UnsupportedNode.type_infer = type_infer_UnsupportedNode


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

# Well, it's more complicated than that... (sequences...)

def type_infer_EAdd(expr, ctx):
    left_type = expr.left.type_infer(ctx)
    if not left_type:
        return None

    if isinstance(left_type, (NumberType, IntType, FloatType)):    
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

    elif isinstance(left_type, StrType):
        right_type = type_expect(ctx, expr.right, StrType())
        if not right_type:
            return None

        return StrType()

    elif isinstance(left_type, ListType):
        right_type = expr.right.type_infer(ctx)
        if not right_type:
            return None

        if not isinstance(right_type, ListType):
            ctx.add_type_error(TypeComparisonError(ctx.function_def, left_type, expr.right, right_type,
                                                   tr("Expecting a list")))
            return None

        if left_type.elem_type != right_type.elem_type:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, left_type.elem_type, expr.right, right_type.elem_type,
                                                   tr("Expecting a list with elements of type: {}").format(left_type.elem_type)))
            return None

        return left_type

    else:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, ListType(), expr.left, left_type,
                                               tr("Expecting a list")))
        return None
            
    

        

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

def type_infer_EUSub(expr, ctx):
    operand_type = type_expect(ctx, expr.operand, NumberType())
    if not operand_type:
        return None

    return operand_type

EUSub.type_infer = type_infer_EUSub


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

def type_infer_EFloorDiv(expr, ctx):
    left_type = type_expect(ctx, expr.left, IntType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, IntType())
    if not right_type:
        return None

    return IntType()

EFloorDiv.type_infer = type_infer_EFloorDiv

def type_infer_EMod(expr, ctx):
    left_type = type_expect(ctx, expr.left, IntType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, IntType())
    if not right_type:
        return None

    return IntType()

EMod.type_infer = type_infer_EMod

def type_infer_EPow(expr, ctx):
    target_type = expr.left.type_infer(ctx)
    if target_type is None:
        return None

    if isinstance(target_type, IntType) \
       or isinstance(target_type, FloatType) \
       or isinstance(target_type, NumberType):
        exponent_type = type_expect(ctx, expr.right, IntType())
        if exponent_type is None:
            return None
        return IntType()
    else: # not a numeric type
       return type_expect(ctx, expr.left, NumberType())

EPow.type_infer = type_infer_EPow


def type_infer_EVar(var, ctx):
    # check if the variable is dead
    if var.name in ctx.dead_variables:
        ctx.add_type_error(DeadVariableUseError(var.name, var))
        return None

    # check if the var is a parameter
    if ctx.param_env and var.name in ctx.param_env:
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

def type_infer_EStr(estr, ctx):
    return StrType()

EStr.type_infer = type_infer_EStr

def type_infer_ETrue(node, ctx):
    return BoolType()

ETrue.type_infer = type_infer_ETrue

def type_infer_EFalse(node, ctx):
    return BoolType()

EFalse.type_infer = type_infer_EFalse

def type_infer_BoolOp(node, ctx):
    for operand in node.operands:
        operand_type = type_expect(ctx, operand, BoolType())
        if not operand_type:
            return None
    return BoolType()

EAnd.type_infer = type_infer_BoolOp
EOr.type_infer = type_infer_BoolOp

def type_infer_ENot(node, ctx):
    operand_type = type_expect(ctx, node.operand, BoolType())
    if not operand_type:
        return None
    return BoolType()

ENot.type_infer = type_infer_ENot

def type_infer_ENone(node, ctx):
    return NoneTypeType()

ENone.type_infer = type_infer_ENone

def type_infer_ECall(call, ctx):
    # step 1 : fetch the signature of the called function
    if call.full_fun_name in ctx.global_env:
        method_call = False
        signature = ctx.global_env[call.full_fun_name]
        arguments = call.arguments
    elif "." + call.fun_name in { ".append" } and not call.multi_receivers:
        method_call = True
        signature = ctx.global_env["." + call.fun_name]
        arguments = []
        arguments.append(call.receiver)
        arguments.extend(call.arguments)
    else:
        ctx.add_type_error(UnknownFunctionError(ctx.function_def, call))
        return None

    # step 1bis : we rename the type parameters to avoid any nameclash
    rename_map = {}
    signature = signature.rename_type_variables(rename_map)
    #print("rename_map = {}".format(rename_map))
    #print(repr(signature))

    # step 2 : check the call arity
    if len(signature.param_types) != len(arguments):
        ctx.add_type_error(CallArityError(ctx.function_def, method_call, signature, call))
        return None

    # step 3 : check the argument types
    num_arg = 1
    ctx.call_type_env.append(dict())  # the type environment for calls (for generic functions) 
    for (arg, param_type) in zip(arguments, signature.param_types):
        #print("arg={}".format(arg))
        #print("param_type={}".format(param_type))
        if isinstance(param_type, TypeVariable):
            if param_type.var_name in ctx.call_type_env[-1]:
                arg_type = type_expect(ctx, arg, ctx.call_type_env[-1][param_type.var_name])
                if arg_type is None:
                    #ctx.add_type_error(CallArgumentError(ctx.function_def, method_call, call, num_arg, arg, ctx.call_type_env[param_type.var_name]))
                    ctx.call_type_env.pop()
                    return None
            else: # bind the type variable
                arg_type = arg.type_infer(ctx)
                if arg_type is None:
                    # XXX: add an error ?
                    return None

                ctx.call_type_env[-1][param_type.var_name] = arg_type

        else: # not a type variable
            arg_type = type_expect(ctx, arg, param_type)
            if arg_type is None:
                #ctx.add_type_error(CallArgumentError(ctx.function_def, method_call, call, num_arg, arg, param_type))
                ctx.call_type_env.pop()
                return None
        num_arg += 1

    # step 4 : return the return type
    if ctx.call_type_env[-1]:
        nret_type = signature.ret_type.subst(ctx.call_type_env[-1])
        ctx.call_type_env.pop()
        return nret_type
    else:
        ctx.call_type_env.pop()
        return signature.ret_type

ECall.type_infer = type_infer_ECall

def type_infer_ECompare(ecomp, ctx):
    for cond in ecomp.conds:
        if not cond.type_check(ctx, ecomp):
            return None

    return BoolType()

ECompare.type_infer = type_infer_ECompare

def type_check_Condition(cond, ctx, compare):
    left_type = cond.left.type_infer(ctx)
    if left_type is None:
        return False
    if type_expect(ctx, cond.right, left_type, raise_error=False) is None:
        ctx.add_type_error(CompareConditionError(compare, cond))
        return False
    return True

Condition.type_check = type_check_Condition

def type_infer_ETuple(tup, ctx):
    if not tup.elements:
        ctx.add_type_error(EmptyTupleError(tup))
        return None

    element_types = []
    for element in tup.elements:
        element_type = element.type_infer(ctx)
        if not element_type:
            return None
        element_types.append(element_type)

    return TupleType(element_types)

ETuple.type_infer = type_infer_ETuple

def type_infer_EList(lst, ctx):
    lst_type = None
    if not lst.elements:
        return ListType()

    for element in lst.elements:
        element_type = element.type_infer(ctx)
        if element_type is None:
            return None
        #print("----\nelement type={}".format(element_type))
        #print("lst type={}\n----".format(lst_type))
        if lst_type is None:
            lst_type = element_type
        else:
            if not lst_type.type_compare(ctx, element, element_type, raise_error=False):
                ctx.add_type_error(HeterogeneousElementError('list', lst, lst_type, element_type, element))
                return None

    return ListType(lst_type)

EList.type_infer = type_infer_EList

def type_infer_Indexing(indexing, ctx):
    subject_type = indexing.subject.type_infer(ctx)
    if subject_type is None:
        return None

    if isinstance(subject_type, SequenceType) \
         or isinstance(subject_type, ListType):
        sequential = True
        result_type = subject_type.elem_type

    elif isinstance(subject_type, StrType):
        sequential = True
        result_type = StrType() # XXX: typical python twist !

    elif isinstance(subject_type, DictType):
        # TODO : dict typing
        sequential = False
        raise NotImplementedError("Dictionary typing not (yet) supported")

    else:
        ctx.add_type_error(IndexingError(indexing, subject_type))
        return None

    if sequential:
        if type_expect(ctx, indexing.index, IntType(), raise_error=False) is None:
            ctx.add_type_error(IndexingSequenceNotNumeric(indexing.index))
            return None
    else: # dictionary
        if type_expect(ctx, indexing.index, key_type, raise_error=False) is None:
            ctx.add_type_error(IndexingDictKeyTypeError(indexing.index))
            return None

    return result_type

Indexing.type_infer = type_infer_Indexing

def type_infer_Slicing(slicing, ctx):
    subject_type = slicing.subject.type_infer(ctx)
    if subject_type is None:
        return None

    if isinstance(subject_type, SequenceType) \
       or isinstance(subject_type, ListType):
        result_type = subject_type

    elif isinstance(subject_type, StrType):
        result_type = StrType() # XXX: typical python twist !
        
    else:
        ctx.add_type_error(SlicingError(slicing, subject_type))
        return None

    # check slice arguments

    if slicing.lower and not type_expect(ctx, slicing.lower, IntType(), raise_error=True):
        return None

    if slicing.upper and not type_expect(ctx, slicing.upper, IntType(), raise_error=True):
        return None

    if slicing.step and not type_expect(ctx, slicing.step, IntType(), raise_error=True):
        return None

    return result_type

Slicing.type_infer = type_infer_Slicing
    

######################################
# Type comparisons                   #
######################################

def type_expect(ctx, expr, expected_type, raise_error=True):
    expr_type = expr.type_infer(ctx)
    if not expr_type:
        return None
    #print("[type_expect] expected_type={}".format(expected_type))
    if not expected_type.type_compare(ctx, expr, expr_type, raise_error):
        #ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Mismatch type '{}' expecting: {} ").format(expr_type, expected_type)))
        return None
    return expr_type

def type_compare_Anything(expected_type, ctx, expr, expr_type, raise_error=True):
    # everything is compatible with anything
    return True

Anything.type_compare = type_compare_Anything

def type_compare_NumberType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, NumberType) \
       or isinstance(expr_type, IntType) \
       or isinstance(expr_type, FloatType): 
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Number")))

    return False

NumberType.type_compare = type_compare_NumberType

def type_compare_IntType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, IntType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an int")))

    return False

IntType.type_compare = type_compare_IntType

def type_compare_FloatType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, FloatType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a float")))

    return False

FloatType.type_compare = type_compare_FloatType

def type_compare_BoolType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, BoolType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Bool (type bool)")))

    return False

BoolType.type_compare = type_compare_BoolType

def type_compare_StrType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, StrType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a string (type str)")))

    return False

StrType.type_compare = type_compare_StrType

def type_compare_ListType(expected_type, ctx, expr, expr_type, raise_error=True):
    #print("expected_type={}".format(expected_type))
    #print("expr_type={}".format(expr_type))

    if not isinstance(expr_type, ListType):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a list")))
        return False

    if expr_type.is_emptylist():
        return True

    if expected_type.is_emptylist():
        return True

    return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

ListType.type_compare = type_compare_ListType

def type_compare_IterableType(expected_type, ctx, expr, expr_type, raise_error=True):
    #print("expected_type={}".format(expected_type))
    #print("expr_type={}".format(expr_type))
    #print("expr={}".format(expr))

    if isinstance(expr_type, ListType) and expr_type.is_emptylist():
        return True

    if isinstance(expr_type, IterableType) \
       or isinstance(expr_type, SequenceType) \
       or isinstance(expr_type, ListType) \
       or isinstance(expr_type, SetType):
        return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

    elif isinstance(expr_type, StrType):
        return expected_type.elem_type.type_compare(ctx, expr, StrType(), raise_error)

    elif isinstance(expr_type, DictType):
        raise NotImplementedError("type_compare_IterableType (dict type)")
    else:
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an Iterable (Sequence, list, string, set or dictionnary)")))
        return False

IterableType.type_compare = type_compare_IterableType

def type_compare_SequenceType(expected_type, ctx, expr, expr_type, raise_error=True):
    #print("expected_type={}".format(expected_type))
    #print("expr_type={}".format(expr_type))
    #print("expr={}".format(expr))

    if isinstance(expr_type, SequenceType) \
       or isinstance(expr_type, ListType) \
       or isinstance(expr_type, SetType):
        return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

    elif isinstance(expr_type, StrType):
        return expected_type.elem_type.type_compare(ctx, expr, StrType(), raise_error)

    else:
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Sequence (list or string)")))
        return False

SequenceType.type_compare = type_compare_SequenceType


def type_compare_TypeVariable(expected_type, ctx, expr, expr_type, raise_error=True):
    if expected_type.is_call_variable():
        if expected_type.var_name in ctx.call_type_env[-1]:
            real_expected_type = ctx.call_type_env[-1][expected_type.var_name]
            if real_expected_type == expr_type:
                return True
            # not equal
            if raise_error:
                ctx.add_type_error(TypeComparisonError(ctx.function_def, real_expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:],real_expected_type, expr_type)))
            return False
        else: # register type as type parameter:
            ctx.call_type_env[-1][expected_type.var_name] = expr_type
            return True
    else: # not a call variable
        if expected_type == expr_type:
            return True
        else:
            if raise_error:
                ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:], expected_type, expr_type)))
        return False

TypeVariable.type_compare = type_compare_TypeVariable

def type_compare_NoneTypeType(expected_type, ctx, expr, expr_type, raise_error=True):
    if not isinstance(expr_type, NoneTypeType):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting value None")))
        return False

    return True

NoneTypeType.type_compare = type_compare_NoneTypeType

def type_compare_OptionType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, NoneTypeType):
        return True

    val_type = expected_type.elem_type.type_compare(ctx, expr, expr_type, raise_error=False)
    if not val_type:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting value None or of type: {}").format(expected_type.elem_type)))
        return False

    return True

OptionType.type_compare = type_compare_OptionType

def type_compare_TupleType(expected_type, ctx, expr, expr_type, raise_error=True):
    if not isinstance(expr_type, TupleType):
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a tuple")))
        return False

    if len(expr_type.elem_types) != len(expected_type.elem_types):
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a tuple of size '{}' but found: {}").format(len(expected_type.elem_types)
                                                                                                                                                           , len(expr_type.elem_types))))
        return False

    for (expected_elem_type, expr_elem_type) in zip(expected_type.elem_types, expr_type.elem_types):
        if not expected_elem_type.type_compare(ctx, expr, expr_elem_type, raise_error):
            return False

    return True

TupleType.type_compare = type_compare_TupleType

######################################
# Standard imports                   #
######################################

BUILTINS_IMPORTS = {
    'len' : function_type_parser("Iterable[α] -> int").content
    ,'print' : function_type_parser("Ω -> NoneType").content
    ,'range' : function_type_parser("int * int -> Iterable[int]").content
    , '.append' : function_type_parser("list[α] * α -> NoneType").content
}

MATH_IMPORTS = {
    'math.sqrt' : function_type_parser("Number -> float").content
}

REGISTERED_IMPORTS = {
    '' : BUILTINS_IMPORTS
    , 'math' : MATH_IMPORTS
}


## All the possible kinds of error follow

class UnsupportedImportError(TypeError):
    def __init__(self, import_name, import_ast):
        self.import_name = import_name
        self.import_ast = import_ast

    def fail_string(self):
        return "UnsupportedImportError[{}]@{}:{}".format(self.import_name, self.import_ast.ast.lineno, self.import_ast.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Import problem'), line=self.import_ast.ast.lineno
                                    , offset=self.import_ast.ast.col_offset
                                    , details=tr("the module '{}' is not supported in Python101").format(self.import_name))


    def is_fatal(self):
        return True

class SignatureParseError(TypeError):
    def __init__(self, fun_name, fun_def, signature):
        self.fun_name = fun_name
        self.fun_def = fun_def
        self.signature = signature

    def fail_string(self):
        return "SignatureParseError[{}]@{}:{}".format(self.fun_name, self.fun_def.ast.lineno, self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Signature problem"), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , details=tr("I don't understand the signature of function '{}'").format(self.fun_name))

    def is_fatal(self):
        return False


class FunctionArityError(TypeError):
    def __init__(self, func_def, signature):
        self.func_def = func_def
        self.signature = signature

    def is_fatal(self):
        return True

    def fail_string(self):
        return "FunctionArityError[{},{}/{}]@{}:{}".format(self.func_def.name
                                                           , len(self.func_def.parameters)
                                                           , len(self.signature.param_types)
                                                           , self.func_def.ast.lineno
                                                           , self.func_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Function arity issue"), self.func_def.ast.lineno, self.func_def.ast.col_offset
                                    , tr("the signature of function '{}' defines {} parameters, but there are {} effectively: {}").
                                    format(self.func_def.name
                                           , len(self.signature.param_types)
                                           , len(self.func_def.parameters)
                                           , "({})".format(", ".join(self.func_def.parameters))))


class UnsupportedNodeError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node
        #print("Unsupported Node:")
        #print(astpp.dump(self.node.ast))

    def is_fatal(self):
        return False

    def fail_string(self):
        return "UnsupportedNodeError[{}]@{}:{}".format(str(self.node.ast.__class__.__name__)
                                                       , self.node.ast.lineno
                                                       , self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Not-Python101'), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("this construction is not available in Python101 (try expert mode for standard Python)"))

class DisallowedDeclarationError(TypeError):
    def __init__(self, in_function, node):
        self.in_function = in_function
        self.node = node

    def is_fatal(self):
        return True

class DeclarationError(TypeError):
    def __init__(self, in_function, node, category, lineno, explain):
        self.in_function = in_function
        self.node = node
        self.category = category
        self.lineno = lineno
        self.explain = explain

    def fail_string(self):
        return "DeclarationError[{}]@{}:{}".format(self.category
                                                   , self.lineno
                                                   , self.node.ast.col_offset)

    def is_fatal(self):
        return False

    def report(self, report):
        col_offset = self.node.ast.col_offset
        report.add_convention_error('error', tr('Declaration problem'), self.lineno, col_offset, self.explain)

class UnknownVariableError(TypeError):
    def __init__(self, in_function, var):
        self.in_function = in_function
        self.var = var

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnknownVariableError[{}]@{}:{}".format(self.var.name
                                                       , self.var.ast.lineno
                                                       , self.var.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Variable problem"), self.var.ast.lineno, self.var.ast.col_offset
                                    , tr("there is such variable of name '{}'").format(self.var.name))

class TypeComparisonError(TypeError):
    def __init__(self, in_function, expected_type, expr, expr_type, explain):
        self.in_function = in_function
        self.expected_type = expected_type
        self.expr = expr
        self.expr_type = expr_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "TypeComparisonError[{}/{}]@{}:{}".format(self.expected_type, self.expr_type, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Incompatible types"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("Expecting type {} but found {} instead").format(self.expected_type, self.expr_type))

class UnsupportedNumericTypeError(TypeError):
    def __init__(self, in_function, num):
        self.in_function = in_function
        self.num = num

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnsupportedNumericTypeError[{}]@{}:{}".format(self.num.value, self.num.ast.lineno, self.num.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Number problem"), self.num.ast.lineno, self.num.ast.col_offset
                                    , tr("this numeric value is not supported in Python 101: {} ({})").format(self.num.value, type(self.num.value)))

class WrongReturnTypeError(TypeError):
    def __init__(self, in_function, ret, ret_type, partial_function):
        self.in_function = in_function
        self.ret = ret
        self.ret_type = ret_type
        self.partial_function = partial_function

    def is_fatal(self):
        return True

class UnknownFunctionError(TypeError):
    def __init__(self, in_function, call):
        self.in_function = in_function
        self.call = call

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnknownFunctionError[{}]@{}:{}".format(self.call.full_fun_name, self.call.ast.lineno, self.call.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Call problem"), self.call.ast.lineno, self.call.ast.col_offset
                                    , tr("I don't know any function named '{}'").format(self.call.full_fun_name))

class CallArityError(TypeError):
    def __init__(self, in_function, method_call, signature, call):
        self.in_function = in_function
        self.signature = signature
        self.call = call
        self.method_call = method_call

    def is_fatal(self):
        return True
    
class CallArgumentError(TypeError):
    def __init__(self, in_function, method_call, call, num_arg, arg, param_type):
        self.in_function = in_function
        self.method_call = method_call
        self.call = call
        self.num_arg = num_arg
        self.arg = arg
        self.param_type = param_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "CallArgumentError[{}]@{}:{}".format(self.num_arg, self.arg.ast.lineno, self.arg.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Call problem"), self.arg.ast.lineno, self.arg.ast.col_offset
                                    , tr("the {}-th argument in call to function '{}' is erroneous").format(self.num_arg
                                                                                                           , self.call.fun_name))

class TestCaseError(TypeError):
    def __init__(self, test_case, expr_type):
        self.test_case = test_case
        self.expr_type = expr_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "TestCaseError[{}]@{}:{}".format(self.expr_type.__class__.__name__, self.test_case.ast.lineno, self.test_case.ast.col_offset)

class CompareConditionError(TypeError):
    def __init__(self, compare, cond):
        self.compare = compare
        self.cond = cond

    def is_fatal(self):
        return True

    def fail_string(self):
        return "CompareConditionError@{}:{}".format(self.compare.ast.lineno, self.compare.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Comparison error"), self.compare.ast.lineno, self.compare.ast.col_offset
                                    , tr("The two operands of the comparision should have the same type"))

class DeadVariableUseError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return False

    def fail_string(self):
        return "DeadVariableUseError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of a variable that is not in scope (Python101 scoping rule)"))

class IndexingError(TypeError):
    def __init__(self, indexing, subject_type):
        self.indexing = indexing
        self.subject_type = subject_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "IndexingError[{}]@{}:{}".format(self.subject_type, self.indexing.ast.lineno, self.indexing.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad indexing"), self.indexing.ast.lineno, self.indexing.ast.col_offset
                                    , tr("One can only index a sequence or a dictionnary, not a '{}'").format(self.subject_type))


class IndexingSequenceNotNumeric(TypeError):
    def __init__(self, index):
        self.index = index

    def is_fatal(self):
        return True

    def fail_string(self):
        return "IndexingSequenceNotNumeric[]@{}:{}".format(self.index.ast.lineno, self.index.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad index"), self.index.ast.lineno, self.index.ast.col_offset
                                    , tr("Sequence index must be an integer"))


class HeterogeneousElementError(TypeError):
    def __init__(self, container_kind, container, container_type, element_type, element):
        self.container_kind = container_kind
        self.container = container
        self.element_type = element_type
        self.container_type = container_type
        self.element = element

    def is_fatal(self):
        return True

    def fail_string(self):
        return "HeterogenousElementError[{}]@{}:{}".format(self.element_type, self.element.ast.lineno, self.element.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Heterogeneous elements (Python101 restriction)"), self.element.ast.lineno, self.element.ast.col_offset
                                    , tr("All elements of must be of the same type '{}' but this element has incompatible type: {}").format(self.container_type, self.element_type))


class TupleDestructArityError(TypeError):
    def __init__(self, destruct, expected_tuple_type, expected_arity, actual_arity):
        self.destruct = destruct
        self.expected_arity = expected_arity
        self.actual_arity = actual_arity
        
    def is_fatal(self):
        return True

    def fail_string(self):
        return "TupleDestructArityError[{}]@{}:{}".format(self.expected_arity, self.destruct.ast.lineno, self.destruct.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Tuple destruct error"), self.destruct.ast.lineno, self.destruct.ast.col_offset
                                    , tr("Wrong number of variables to destruct tuple, expecting {} variables but {} given").format(self.expected_arity, self.actual_arity))
    
    
def typecheck_from_ast(ast, filename=None, source=None):
    prog = Program()
    prog.build_from_ast(ast, filename, source)
    ctx = prog.type_check()
    return ctx

def typecheck_from_file(filename):
    prog = Program()
    prog.build_from_file(filename)
    ctx = prog.type_check()
    return ctx

if __name__ == '__main__':

    ctx = typecheck_from_file("../../test/progs/01_aire_KO_14.py")
    print(repr(ctx))
