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

    from .translate import tr

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
        self.dead_variables = set()
        self.parent_stack = None
        self.local_env = None

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
        self.local_env = {}

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

    # first step : fill the global environment

    # first register the builtins
    ctx.register_import(REGISTERED_IMPORTS[''])

    # then register the imports
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

    # fourth step: type-check test assertions
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

def type_check_Assign(assign, ctx):
    # first let's see if the variable is dead
    if assign.var_name in ctx.dead_variables:
        ctx.add_type_error(DeadVariableUse(assign.var_name, assign))
        return False


    # Step 1: distinguish between initialization and proper assignment
    if assign.var_name not in ctx.local_env:
        # initialization
        # Step 2a) check if declaration is allowed here  <<<=== XXX: This convention is maybe too restrictive (?)
        # if not ctx.allow_declarations:
        #     ctx.add_type_error(DisallowedDeclaration(ctx.function_def, assign))
        #     return
        # Step 3a) fetch declared type
        declared_type = fetch_declaration_type(ctx, assign)
        if declared_type is None:
            return False

        # Step 4a) infer type of initialization expression
        expr_type = assign.expr.type_infer(ctx)
        if expr_type is None:
            return False
        # Step 5a) compare inferred type wrt. declared type
        if not declared_type.type_compare(ctx, assign.expr, expr_type):
            return False
        # Step 6a) register declared type in environment
        ctx.local_env[assign.var_name] = (declared_type, ctx.fetch_scope_mode())
        return True

    else: # proper assignment

        # XXX: check if the student does not try a new declaration ?

        declared_type, scope_mode = ctx.local_env[assign.var_name]

        expr_type = assign.expr.type_infer(ctx)
        if expr_type is None:
            return False

        if not declared_type.type_compare(ctx, assign.expr, expr_type):
            return False

        return True

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

def fetch_declaration_type(ctx, assign):
    lineno = assign.ast.lineno
    decl_line = ctx.prog.get_source_line(lineno-1).strip()

    #print(decl_line)
    if (not decl_line) or decl_line[0] != '#':
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'header-char', tr("Missing variable declaration '{}'").format(assign.var_name)))
        return None
    decl_line = decl_line[1:].strip()
    var_name, decl_line = parse_var_name(decl_line)
    #print(var_name)
    #print(assign.var_name)
    if var_name != assign.var_name:
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'var-name', tr("Wrong variable name in declaration, it should be '{}'").format(assign.var_name)))
        return None
    if (not decl_line) or decl_line[0] != ':':
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'colon', tr("Missing ':' character before variable type declaration")))
        return None
    decl_line = decl_line[1:].strip()
    decl_type = type_expression_parser(decl_line)
    #print("rest='{}'".format(decl_line[decl_type.end_pos.offset:]))
    if decl_type.iserror: # or decl_line[decl_type.end_pos.offset:]!='': (TODO some sanity check ?)
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'parse', tr("I don't understand the declared type for variable '{}'").format(assign.var_name)))
        return None
    remaining = decl_line[decl_type.end_pos.offset:].strip()
    if remaining != '' and not remaining.startswith('('):
        ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'parse', tr("The declared type for variable '{}' has strange appended string: {}").format(assign.var_name, remaining)))
    #print(repr(decl_type))
    #print(decl_type.content)
    return decl_type.content

Assign.type_check = type_check_Assign

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
    elif isinstance(call_type, NoneType):
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

def type_infer_EVar(var, ctx):
    # check if the variable is dead
    if var.name in ctx.dead_variables:
        ctx.add_type_error(DeadVariableUse(var.name, var))
        return None

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

def type_infer_EStr(estr, ctx):
    return StrType()

EStr.type_infer = type_infer_EStr

def type_infer_ETrue(node, ctx):
    return BoolType()

ETrue.type_infer = type_infer_ETrue

def type_infer_EFalse(node, ctx):
    return BoolType()

EFalse.type_infer = type_infer_EFalse

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
    ctx.call_type_env = dict()  # the type environment for calls (for generic functions) 
    for (arg, param_type) in zip(arguments, signature.param_types):
        #print("arg={}".format(arg))
        #print("param_type={}".format(param_type))
        if isinstance(param_type, TypeVariable):
            if param_type.var_name in ctx.call_type_env:
                arg_type = type_expect(ctx, arg, ctx.call_type_env[param_type.var_name])
                if arg_type is None:
                    #ctx.add_type_error(CallArgumentError(ctx.function_def, method_call, call, num_arg, arg, ctx.call_type_env[param_type.var_name]))
                    ctx.call_type_env = None
                    return None
            else: # bind the type variable
                arg_type = arg.type_infer(ctx)
                if arg_type is None:
                    # XXX: add an error ?
                    return None

                ctx.call_type_env[param_type.var_name] = arg_type

        else: # not a type variable
            arg_type = type_expect(ctx, arg, param_type)
            if arg_type is None:
                #ctx.add_type_error(CallArgumentError(ctx.function_def, method_call, call, num_arg, arg, param_type))
                ctx.call_type_env = None
                return None
        num_arg += 1

    # step 4 : return the return type
    if ctx.call_type_env:
        nret_type = signature.ret_type.subst(ctx.call_type_env)
        ctx.call_type_env = None
        return nret_type
    else:
        ctx.call_type_env = None
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


def type_infer_EList(lst, ctx):
    lst_type = None
    if not lst.elements:
        return ListType()

    for element in lst.elements:
        element_type = element.type_infer(ctx)
        if lst_type is None:
            lst_type = element_type
        else:
            if element_type != lst_type:
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
        result_type = StrType # XXX: typical python twist !

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

    return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

ListType.type_compare = type_compare_ListType

def type_compare_IterableType(expected_type, ctx, expr, expr_type, raise_error=True):
    #print("expected_type={}".format(expected_type))
    #print("expr_type={}".format(expr_type))
    #print("expr={}".format(expr))

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
        if expected_type.var_name in ctx.call_type_env:
            real_expected_type = ctx.call_type_env[expected_type.var_name]
            if real_expected_type == expr_type:
                return True
            # not equal
            if raise_error:
                ctx.add_type_error(TypeComparisonError(ctx.function_def, real_expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:],real_expected_type, expr_type)))
            return False
        else: # register type as type parameter:
            ctx.call_type_env[expected_type.var_name] = expr_type
            return True
    else: # not a call variable
        if expected_type == expr_type:
            return True
        else:
            if raise_error:
                ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:], expected_type, expr_type)))
        return False

TypeVariable.type_compare = type_compare_TypeVariable

######################################
# Standard imports                   #
######################################

BUILTINS_IMPORTS = {
    'len' : function_type_parser("Iterable[α] -> int").content
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
    def __init__(self, in_function, node, category, explain):
        self.in_function = in_function
        self.node = node
        self.category = category
        self.explain = explain

    def fail_string(self):
        return "DeclarationError[{}]@{}:{}".format(self.category
                                                   , self.node.ast.lineno if self.category == "header-char" else self.node.ast.lineno-1
                                                   , self.node.ast.col_offset)

    def is_fatal(self):
        return False

    def report(self, report):
        lineno = self.node.ast.lineno
        col_offset = self.node.ast.col_offset
        if self.category == 'header-char':
            report.add_convention_error('error', tr('Declaration problem'), lineno, col_offset, self.explain)
            return
        lineno -= 1
        if self.category == 'var-name' or self.category == 'colon' or self.category == 'parse':
            report.add_convention_error('error', tr('Declaration problem'), lineno, col_offset, self.explain)
        else:
            raise ValueError("Unknown declaration category: '{}' (please report)".format(self.category))


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

class DeadVariableUse(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return False

    def fail_string(self):
        return "DeadVariableUse[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

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
        report.add_convention_error('error', tr("Heterogeneous elements (Python101 restriction)"), self.index.ast.lineno, self.index.ast.col_offset
                                    , tr("All elements of a {} must be of the same type '{}' but this element has incompatible type: {}").format(tr(self.container_kind), self.container_type, self.element_type))

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
