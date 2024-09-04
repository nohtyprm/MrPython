import os.path, sys
import ast

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
    from type_converter import *

    from translate import tr
    from side_effects_utils import *
else:
    from .prog_ast import *
    from .type_ast import *
    from .type_converter import *

    from .translate import tr

    from .side_effects_utils import *

preconditions = dict()      #Dictionnary to save all the function preconditions

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
        self.parent_decl_stack = None
        self.local_env = None
        self.declared_env = None
        self.call_type_env = [] # stack of type environments when calling generic functions
        self.local_env = {}  # will have global variables
        self.declared_env={} #Will receive type declaration only

        self.in_call = False
        self.protected = set()
        self.aliasing = {}
        self.var_def = {}


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
            self.protected.add(param)
            self.add_var_def(param)

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
        if not self.parent_stack:
            self.parent_stack = []
        self.parent_stack.append((parent_node, parent_local_env))
        parent_local_declare = {var_name : var_info for (var_name, var_info) in self.declared_env.items() }
        if not self.parent_decl_stack:
            self.parent_decl_stack = []
        self.parent_decl_stack.append((parent_node, parent_local_declare))

    def pop_parent(self, protected_vars=None):
        if protected_vars is None:
            protected_vars = set()

        if not self.parent_decl_stack:
            raise ValueError("Cannot pop from empty parent declaration stack (please report)")

        _, parent_local_declare = self.parent_decl_stack.pop()
        for (var_name, var_info) in self.declared_env.items():
            if var_name not in parent_local_declare:
                # XXX: barendregt convention too strong ?
                # self.dead_variables.add(var)
                if var_name not in self.local_env and var_name not in protected_vars:
                    self.add_type_error(NotUsedDeclarationWarning(self.function_def, var_name,var_info))

        self.declared_env = parent_local_declare

        if not self.parent_stack:
            raise ValueError("Cannot pop from empty parent stack (please report)")

        # all variables defined within the parent are now disallowed

        _, parent_local_env = self.parent_stack.pop()
        for (var_name, var_info) in self.local_env.items():
            if (var_name, var_info) not in parent_local_env.items():
                if var_name in self.declared_env :
                    parent_local_env[var_name]=var_info
                else:
                    pass
                # XXX: barendregt convention too strong ?
                # self.dead_variables.add(var)

        self.local_env = parent_local_env

        # all variables defined within the parent are now disallowed

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

        self.in_call = False
        self.protected = set()
        self.aliasing = {}
        self.var_def = {}

    def fetch_scope_mode(self):
        # TODO : complete with parent stack
        if not self.parent_stack:
            return 'function'


    #links must be bidirectionnal...
    def add_alias(self, var, aliased):
        tmp = AliasRef(var, self.var_def[var])
        self.aliasing[tmp] = self.aliasing[tmp] | aliased
        for a in aliased:
            self.aliasing[AliasRef(a.ref, self.var_def[a.ref])].add(AliasRef(var, self.var_def[var], copy_deque(a.index_out), copy_deque(a.index_in)))

    def print_alias(self):
        res = ""
        for (L, aliased) in self.aliasing.items():
            res = res + str(L) + "->" + str(aliased)
        print(res)

    def get_alias(self, var_ref):
        if var_ref in self.aliasing:
            return self.aliasing.get(var_ref)
        return set()

    def add_var_def(self, var_name):
        if var_name in self.var_def:
            self.var_def[var_name] += 1
        else:
            self.var_def.update({var_name : 0})
        self.aliasing.update({AliasRef(var_name, self.var_def[var_name]) : set()})

    def __repr__(self):
        return "<TypingContext[genv={}, errors={}]>".format(self.global_env, self.type_errors)

TypingContext.get_all_alias = get_all_alias_ctx

#############################################
# Type checking                             #
#############################################

def type_check_UnsupportedNode(node, ctx):
    print("Error: Type checking not supported for this node")
    import astpp
    print(astpp.dump(node.ast))
    ctx.add_type_error(UnsupportedNodeError(node))

    return False

UnsupportedNode.type_check = type_check_UnsupportedNode

# Takes a program, and returns a
# (possibly empty) list of type errors
def type_check_Program(prog):
    ctx = TypingContext(prog)

    if len(prog.multi_declared_functions) != 0:
        for fun_name in prog.multi_declared_functions:
            ctx.add_type_error(DuplicateMultiFunDeclarationError(prog.multi_declared_functions[fun_name], fun_name))
        return ctx

    # we do not type check a program with unsupported top-level nodes
    for top_def in prog.other_top_defs:
        if isinstance(top_def.ast, ast.FunctionDef):
            ctx.add_type_error(WrongFunctionDefError(top_def))
            return ctx
        else:
            # HACK : (some) top-level commands are allowed (but not checked)
            # TODO : more proper type checking of top-level forms
            #print("top level : {}".format(astpp.dump(top_def.ast)))
            if (isinstance(top_def.ast, ast.Expr)
                and isinstance(top_def.ast.value, ast.Call)
                and ((isinstance(top_def.ast.value.func, ast.Name)
                     and top_def.ast.value.func.id in { "show_image", "print" })
                or (isinstance(top_def.ast.value.func, ast.Attribute) # random.seed case
                    and top_def.ast.value.func.attr == "seed"))):
                pass # do nothing
            else:
                ctx.add_type_error(UnsupportedTopLevelNodeError(top_def))
                return ctx

    # type checking begins here

    # first step : extract type definitions from global_vars

    declared_global_vars = set()
    for global_var in prog.global_vars:
        if isinstance(global_var, DeclareVar):
            # TODO: track duplicate global variable declaractions here ?
            if global_var.target.var_name in declared_global_vars:
                ctx.add_type_error(DuplicateMultiAssignError(global_var.ast.lineno, global_var.target.var_name))
                return ctx
            declared_global_vars.add(global_var.target.var_name)

    new_global_vars = []
    for global_var in prog.global_vars:
        to_remove = False
        if isinstance(global_var, Assign) and isinstance(global_var.target, LHSVar) \
           and hasattr(global_var.ast, "value") and global_var.target.var_name not in declared_global_vars:
            ok, type_annotation = type_converter(global_var.ast.value)
            if ok:
                to_remove = True
                type_name = global_var.target.var_name
                if type_name in ctx.type_defs:
                    ctx.add_type_error(DuplicateTypeDefError(global_var.ast.lineno, type_name))
                    return ctx

                type_def, unknown_alias = type_annotation.unalias(ctx.type_defs)
                if type_def is None:
                    if check_if_roughly_type_expr(global_var.ast.value):
                        ctx.add_type_error(UnknownTypeAliasError(type_annotation, unknown_alias, global_var.expr.ast.lineno, global_var.expr.ast.col_offset))
                        return ctx
                    else:
                        to_remove = False
                else:
                    ctx.type_defs[type_name] = type_def
        if not to_remove:
            new_global_vars.append(global_var)

    prog.global_vars = new_global_vars

    # second step :  fill the global environment

    # first register the builtins
    ctx.register_import(REGISTERED_IMPORTS[''])

    # then register the imports
    for import_name in prog.imports:
        if import_name in REGISTERED_IMPORTS:
            ctx.register_import(REGISTERED_IMPORTS[import_name])
            # HACK : import the math.pi constant  (the only constant)
            if import_name == "math":
                ctx.local_env['math.pi'] = (FloatType(), "global")
                ctx.local_env['math.e'] = (FloatType(), "global")
        else:
            ctx.add_type_error(UnsupportedImportError(import_name, prog.imports[import_name]))
            return ctx

    # third step : process each function to fill the global environment
    for (fun_name, fun_def) in prog.functions.items():
        if fun_name in { "add", "append"
                         , "triangle", "draw_triangle", "ellipse", "fill_ellipse"}:
            ctx.add_type_error(ReservedFunctionNameError(fun_def, fun_def.ast.lineno, fun_def.ast.col_offset))
            return ctx

        if fun_def.docstring is None:
            ctx.add_type_error(NoFunctionDocWarning(fun_def))

        if fun_def.returns is None:
            ctx.add_type_error(MissingReturnTypeError(fun_def, fun_def.ast.lineno, fun_def.ast.col_offset))
            return ctx

        ok, fun_type_ast = fun_type_converter(fun_def)
        if not ok:
            ctx.add_type_error(TypeExprParseError(fun_def.ast.lineno, fun_def.ast.col_offset, fun_type_ast))
            return ctx

        fun_type, unknown_alias = fun_type_ast.unalias(ctx.type_defs)
        if fun_type is None:
            ctx.add_type_error(UnknownTypeAliasError(fun_type_ast, unknown_alias, fun_def.ast.lineno, fun_def.ast.col_offset))
            return ctx
        else:
            ctx.register_function(fun_name, fun_type, fun_def)

    # fourth step : type-check each function
    for (fun_name, fun_def) in ctx.functions.items():
        fun_def.type_check(ctx)
        if ctx.fatal_error:
            return ctx

    # fifth step: process each global variable definitions
    # (should not be usable from functions so it comes after)
    for global_var in prog.global_vars:
        global_var.type_check(ctx, global_scope=True)
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
    #Ici modifier : Func type converter
    signature = ctx.global_env[func_def.name]
    #print("signature = ", repr(signature))

    # Step 0: check unhashables
    result = signature.fetch_unhashable()
    if result is not None:
        ctx.add_type_error(FunctionUnhashableError(func_def, result))
        return

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

    # step 3 : type-check preconditions 
    preconditions_ok = []   #List of parsed preconditions
    
    for (precondition, precondition_ast) in func_def.preconditions:
        initCtxErrorsLen = len(ctx.type_errors)
        precondition_type = type_expect(ctx, precondition, BoolType(), False)
        if len(ctx.type_errors) != initCtxErrorsLen:
            for i in range(len(ctx.type_errors)):
                #To delete the undefined var problem in preconditions
                if(isinstance(ctx.type_errors[i],UnknownVariableError)):
                    poped = ctx.type_errors[i]
                    ctx.type_errors.remove(poped)
                    ctx.add_type_error(UndefinedVarInPreconditionWarning(func_def, poped.var, precondition_ast.lineno))
                #Catch all potential errors in precondition
                else:
                    poped = ctx.type_errors[i]
                    ctx.type_errors.remove(poped)
                    ctx.add_type_error(ErrorInPreconditionWarning(func_def, precondition_ast.lineno))

        else:
            if precondition_type is None:
                ctx.add_type_error(FunctionPreconditionWarning(func_def, precondition.type_infer(ctx), precondition_ast.lineno))
            else:
                body = precondition_ast.body
                body.lineno = precondition_ast.lineno
                # Very important to sync start_lineno and end_lineno to avoid case of start_lineno > end_lineno
                body.end_lineno = body.lineno
                preconditions_ok.append(body)

    preconditions[func_def.name] = preconditions_ok
    
    # Step 4 : type-check body
    ctx.push_parent(func_def)

    ctx.nb_returns = 0  # counting the number of returns encountered
    local_vars = set()  #save the checked local variables here
    for instr in func_def.body:
        if isinstance(instr, UnsupportedNode):
            ctx.add_type_error(UnsupportedNodeError(instr))
            # we abort the type-checking of this function
            ctx.nb_returns = 0
            #ctx.pop_parent()
            ctx.unregister_function_def()
            return

        #we abort the type-checking of this function if a local var is declared multiple times
        if isinstance(instr, DeclareVar):
            if instr.target.var_name in local_vars:
                ctx.add_type_error(DuplicateMultiAssignError(instr.ast.lineno, instr.target.var_name))
                return ctx
            local_vars.add(instr.target.var_name)

        #print(repr(instr))
        instr.type_check(ctx)
        if ctx.fatal_error:
            ctx.nb_returns = 0
            #ctx.pop_parent()
            ctx.unregister_function_def()
            return

    if ctx.nb_returns == 0 and not isinstance(signature.ret_type, NoneTypeType):
        ctx.add_type_error(NoReturnInFunctionError(func_def))

    ctx.pop_parent()
    ctx.unregister_function_def()

FunctionDef.type_check = type_check_FunctionDef

def parse_var_name(declaration):
    vdecl = ""
    allow_colon = False
    for i in range(0, len(declaration)):
        if declaration[i] == ':':
            if allow_colon:
                return (vdecl, declaration[i:])
            else:
                return (None, tr("Missing variable name before ':'"))
        elif not declaration[i].isspace():
            vdecl += declaration[i]
            allow_colon = True
        else: # a space character
            pass

    return (None, tr("Missing ':' character before variable type declaration"))

def fetch_assign_mypy_types(ctx, assign_target,annotation, strict=False):

    lineno = assign_target.ast.lineno

    var_name = assign_target.var_name
    ok, decl_type = type_converter(annotation)
    if not ok:
        ctx.add_type_error(TypeExprParseError(lineno, assign_target.ast.col_offset, decl_type))
        return None

    declared_types = dict()

    if var_name == "_":
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("The special variable '_' cannot be declared")))
        return None

    udecl_type, unknown_alias = decl_type.unalias(ctx.type_defs)

    if udecl_type is None:
        ctx.add_type_error(UnknownTypeAliasError(decl_type, unknown_alias, lineno, assign_target.ast.col_offset))
        return None
    else:
        declared_types[var_name] = udecl_type

    return declared_types

def fetch_assign_declared_mypy_types(ctx, assign_target, strict = False, only_warning=False):
    lineno = assign_target.ast.lineno

    vars = []
    if isinstance(assign_target, LHSTuple):
        vars = assign_target.variables()
    else:
        vars = [assign_target]

    declared_types = dict()

    for var in vars:
        var_name = var.var_name
        if var_name not in ctx.declared_env:
            if var_name != "_" and strict:
                if not only_warning:
                    ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("Missing variable declaration for variable: {}").format(var_name)))
                    return None
                else: # only warning
                    ctx.add_type_error(DeclarationWarning(ctx.function_def, assign_target, 'var-name', lineno, tr("Missing variable declaration for variable: {}").format(var_name)))
                continue
            else:
                continue

        decl_type, idk = ctx.declared_env[var_name]
        if decl_type is None:
            ctx.add_type_error(TypeExprParseError(lineno, assign_target.ast.col_offset, annotation.id))
            return None

        udecl_type, unknown_alias = decl_type.unalias(ctx.type_defs)

        if udecl_type is None:
            ctx.add_type_error(UnknownTypeAliasError(decl_type, unknown_alias, lineno, assign_target.ast.col_offset))
            return None
        else:
            declared_types[var_name] = udecl_type

    return declared_types


def fetch_declared_mypy_types(ctx, declaration_target, annotation, strict = False):
    lineno = declaration_target.ast.lineno
    var_name = declaration_target.var_name
    ok, decl_type = type_converter(annotation)
    if not ok:
        ctx.add_type_error(TypeExprParseError(lineno, declaration_target.ast.col_offset, decl_type))
        return None

    declared_types = dict()
    if var_name == "_":
        ctx.add_type_error(DeclarationError(ctx.function_def, declaration_target, 'var-name', lineno, tr("The special variable '_' cannot be declared")))
        return None

    udecl_type, unknown_alias = decl_type.unalias(ctx.type_defs)

    if udecl_type is None:
        ctx.add_type_error(UnknownTypeAliasError(decl_type, unknown_alias, lineno, declaration_target.ast.col_offset))
        return None
    else:
        declared_types[var_name] = udecl_type

    return declared_types


def fetch_assign_declaration_types(ctx, assign_target, strict=False):
    lineno = assign_target.ast.lineno - 1

    # the required variables (except underscore)
    req_vars = { v.var_name for v in assign_target.variables() if v.var_name != "_" }
    if not req_vars:  # if there is no required var, this means all vars are _'s
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("The special variable '_' cannot be use alone")))
        return None

    declared_types = dict()

    var_name, decl_type, err_cat = parse_declaration_type(ctx, lineno)
    if var_name is None and strict:
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, err_cat, lineno if err_cat not in {"header-char"} else (lineno+1), tr(decl_type)))
        return None

    while var_name is not None:

        if var_name in declared_types:
            ctx.add_type_error(DuplicateMultiAssignError(lineno, var_name))
            return None

        if var_name == "_":
            ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("The special variable '_' cannot be declared")))
            return None

        if var_name not in req_vars: # if not a special var, it must be required
            ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'var-name', lineno, tr("Unused variable name '{}' in declaration").format(var_name)))

        else:
            req_vars.remove(var_name)
            udecl_type, unknown_alias = decl_type.unalias(ctx.type_defs)
            if udecl_type is None:
                ctx.add_type_error(UnknownTypeAliasError(decl_type, unknown_alias, lineno, assign_target.ast.col_offset))
                return None
            else:
                declared_types[var_name] = udecl_type
        lineno -= 1
        var_name, decl_type, err_cat = parse_declaration_type(ctx, lineno)
        if var_name is None and err_cat not in {'header-char', 'colon', 'noerror'} and strict:
            ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, err_cat, lineno, tr(decl_type)))
            return None


    if strict and req_vars: # need all declarations in strict mode
        ctx.add_type_error(DeclarationError(ctx.function_def, assign_target, 'unknown-vars', assign_target.ast.lineno, tr("Variable(s) not declared: {}").format(", ".join((v for v in req_vars)))))
        return None

    return declared_types

def check_linearized_tuple_type(working_var, working_type, declared_types, ctx, expr, strict=False):
    # take care of Optional
    if isinstance(working_type, OptionType):
        # add a warning
        ctx.add_type_error(OptionCoercionWarning(expr, working_type, working_type.elem_type))
        working_type = working_type.elem_type

    if not isinstance(working_var, LHSTuple):
        #check if working_var is an instance of LHSVar
        if isinstance(working_var, LHSVar):

            if working_var.var_name == '_': # just skip this check
                return True

            if working_var.var_name in declared_types:
                var_type = declared_types[working_var.var_name]
                if not var_type.type_compare(ctx, expr, working_type, raise_error=False):
                    ctx.add_type_error(VariableTypeError(expr, working_var, declared_types[working_var.var_name], working_type))
                    return False
                ctx.local_env[working_var.var_name] = (var_type, ctx.fetch_scope_mode())
                return True

            # not declared
            #if strict:
            #    return False
            #else:
            ctx.local_env[working_var.var_name] = (working_type, ctx.fetch_scope_mode())
            return True
        else:
            raise NotSupportedError("Not assignating a variable, please report")
            return False
    elif not isinstance(working_type, TupleType):
        ctx.add_type_error(TupleTypeExpectationError(ctx.function_def, expr, working_type))
        return False

    if working_var.arity() != working_type.size():
        ctx.add_type_error(TupleDestructArityError(expr, working_type, working_type.size(), working_var.arity()))
        return False
    for i in range(working_var.arity()):
        if not check_linearized_tuple_type(working_var.elements[i], working_type.elem_types[i],  declared_types, ctx, expr):
            return False

    return True

def type_check_DeclareVar(declareVar, ctx, global_scope = False):

    mono_assign = False
    for var in declareVar.target.variables():
        if var.var_name in ctx.dead_variables:
            ctx.add_type_error(DeadVariableDefineError(var.var_name, var))
            return False

        # check that the variable is not a parameter
        if ctx.param_env and var.var_name in ctx.param_env:
            ctx.add_type_error(ParameterInAssignmentError(var.var_name, var))
            return False

        if var.var_name in ctx.local_env:
            ctx.add_type_error(ForbiddenMultiAssign(var))
            return False

    declared_types = fetch_declared_mypy_types(ctx, declareVar.target, declareVar.type_annotation, False)
    if declared_types is None:
        declared_types = dict()
    strict = False
    if declareVar.target.arity() == 1:
        strict = True

    working_var = declareVar.target
    if strict:
        if working_var.var_name in declared_types:
            var_type = declared_types[working_var.var_name]
            ctx.declared_env[working_var.var_name] = (var_type, { "lineno" : declareVar.ast.lineno
                                                                  , "col_offset" : declareVar.ast.col_offset})
            return True
        else:
            return True #False
    else:
        ctx.declared_env[working_var.var_name] = (working_type, { "lineno" : declareVar.ast.lineno
                                                                  , "col_offset" : declareVar.ast.col_offset})
        return True

DeclareVar.type_check = type_check_DeclareVar

def type_check_Assign(assign, ctx, global_scope = False):
    # first let's see if the variables are dead
    mono_assign = False # is this an actual assignment (and not an initialization ?)
    declaration = False # does the variable had already been declared?
    lineno = assign.ast.lineno
    for var in assign.target.variables():

        # check that the variable is not "dead"  (out of scope)
        if var.var_name in ctx.dead_variables:
            ctx.add_type_error(DeadVariableDefineError(var.var_name, var))
            return False

        # check that the variable is not a parameter
        if ctx.param_env and var.var_name in ctx.param_env:
            ctx.add_type_error(ParameterInAssignmentError(var.var_name, var))
            return False

        # distinguish between a first assignment (initialization) or a reassignemt (mono_assign)
        if var.var_name in ctx.local_env:
            if assign.target.arity() > 1 or global_scope == True:
                # Multiple assigment is forbidden (only multi-declaration allowed)
                # either for global variables, or for destructuring tuples (distinct from assignment)
                ctx.add_type_error(ForbiddenMultiAssign(var))
                return False
            else:
                mono_assign = True
        #see if the variables already had benn declared
        if var.var_name in ctx.declared_env:
            declaration = True

    if mono_assign:
        expr_type = assign.expr.type_infer(ctx)
        if expr_type is None:
            return False

        assign.side_effect(ctx)

        var_type = ctx.local_env[var.var_name][0]
        if not var_type.type_compare(ctx, assign.expr, expr_type, raise_error=True):
            return False

        # nothing else to do for actual assignment
        return True

    # here we consider an initialization and not an actual assignment

    # next fetch the declared types  (only required for mono-variables)

    if declaration:
        if (not global_scope) and hasattr(assign, "type_annotation"):
            ctx.add_type_error( DuplicateMultiAssignError(lineno,var.var_name))
        # Assignation of variables that have already been declared
        declared_types = fetch_assign_declared_mypy_types(ctx, assign.target,True if assign.target.arity() == 1 else False )

    else: # no priori declaration
        if assign.target.arity() == 1:
            if not hasattr(assign, "type_annotation"):
                ctx.add_type_error(DeclarationError(ctx.function_def, assign, 'missing', lineno, tr("Missing variable declaration for variable: {}").format(var.var_name)))
                return False

            declared_types = fetch_assign_mypy_types(ctx, assign.target,assign.type_annotation, True if assign.target.arity() == 1 else False)
        else:
            declared_types = dict()

    if declared_types is None:
        # XXX: was not an error => declared_types = dict()
        return False

    # next infer type of initialization expression
    expr_type = assign.expr.type_infer(ctx)
    if expr_type is None:
        return False

    strict = False
    # treat the simpler "mono-var" case first
    if assign.target.arity() == 1:
        strict = True

    # here we have a destructured initialization, it is not necessary to declare variables

    if not check_linearized_tuple_type(assign.target, expr_type, declared_types, ctx, assign.target, strict):
        return False

    assign.side_effect(ctx)

    return True

Assign.type_check = type_check_Assign

def type_check_For(for_node, ctx):

    if for_node.has_forbidden_orelse:
        ctx.add_type_error(UnsupportedElseError(for_node))
        return False

    # first let's see if the iter variables are dead or in the local environment
    for var in for_node.target.variables():
        if var.var_name in ctx.dead_variables:
            ctx.add_type_error(DeadVariableDefineError(var.var_name, var))
            return False

        # check that the variable is not a parameter
        if ctx.param_env and var.var_name in ctx.param_env:
            ctx.add_type_error(ParameterInForError(var.var_name, var))
            return False


        if var.var_name in ctx.local_env:
            ctx.add_type_error(IterVariableInEnvError(var.var_name, var))
            return False


    strict = True if for_node.target.arity() == 1 else False
    only_warning = True if for_node.target.arity() == 1 else False
    declared_types = fetch_assign_declared_mypy_types(ctx, for_node.target, strict, only_warning)
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
       or isinstance(iter_type, StrType) \
       or isinstance(iter_type, DictType):

        if isinstance(iter_type, DictType):
            # XXX: it's a hack but it is worth it ...
            iter_type.elem_type = iter_type.key_type

        ctx.push_parent(for_node)

        # === do like in Assign ===
        expr_type = iter_type.elem_type if not isinstance(iter_type, StrType) else StrType()
        # treat the simpler "mono-var" case first
        strict = False
        if for_node.target.arity() == 1:
            strict = True

        if not check_linearized_tuple_type(for_node.target, expr_type, declared_types, ctx, for_node.target, strict):
            ctx.pop_parent()
            return False

        for_node.side_effect(ctx)
        # and now type check the body in the constructed local env

        for instr in for_node.body:
            if not instr.type_check(ctx):
                ctx.pop_parent()
                return False

        ctx.pop_parent()
        return True

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

    udecl_type = decl_type.unalias(ctx.type_defs)
    if udecl_type is None:
        ctx.add_type_error(UnknownTypeAliasError(decl_type, unknown_alias, lineno, iter_node.ast.col_offset))
        return None
    else:
        return udecl_type

def type_check_Return(ret, ctx):
    ctx.nb_returns += 1
    expr_type = ret.expr.type_infer(ctx)
    if not expr_type:
        return False
    if not ctx.return_type.type_compare(ctx, ret.expr, expr_type, raise_error=False):
        ctx.add_type_error(WrongReturnTypeError(ctx.function_def, ctx.return_type, expr_type, ret))
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
    # avoid else clause
    if wnode.has_forbidden_orelse:
        ctx.add_type_error(UnsupportedElseError(wnode))
        return False

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

def type_check_Expr(enode, ctx):
    expr_type = enode.type_infer(ctx)
    if expr_type is None:
        return False

    ctx.add_type_error(ExprAsInstrWarning(enode))
    return True

Expr.type_check = type_check_Expr

def type_check_ECall(enode, ctx):
    call_type = enode.type_infer(ctx)
    if call_type is None:
        return False
    elif isinstance(call_type, NoneTypeType):
        return True
    else: # the return type is not None: it's a warning
        ctx.add_type_error(CallNotNoneWarning(enode, call_type))
        return True

ECall.type_check = type_check_ECall

def type_check_ERange(erange, ctx):
    erange_type = erange.type_infer(ctx)
    if erange_type is None:
        return False
    # the return type is not None: it's a warning
    ctx.add_type_error(CallNotNoneWarning(erange, erange_type))
    return True

ERange.type_check = type_check_ERange

def type_check_Assertion(assertion, ctx):
    # always generate a warning for asserts in functions
    ctx.add_type_error(AssertionInFunctionWarning(ctx.function_def.name, assertion))

    expr_type = type_expect(ctx, assertion.test, BoolType())
    if expr_type is None:
        return False
    return True

Assertion.type_check = type_check_Assertion


def type_check_With(ewith, ctx):
    # push the parent for the scoping rule
    ctx.push_parent(ewith)

    wtype = ewith.call.type_infer(ctx)
    if wtype is None:
        ctx.pop_parent()
        return False

    if ewith.var_name in ctx.dead_variables:
        ctx.add_type_error(DeadVariableDefineError(ewith.var_name, ewith))
        ctx.pop_parent()
        return False

    # check that the variable is not a parameter
    if ctx.param_env and ewith.var_name in ctx.param_env:
        ctx.add_type_error(ParameterInWithError(ewith.var_name, ewith))
        ctx.pop_parent()
        return False

    # same for local environment
    if ewith.var_name in ctx.local_env:
        ctx.add_type_error(WithVariableInEnvError(var.var_name, ewith))
        ctx.pop_parent()
        return False

    ctx.local_env[ewith.var_name] = (wtype, ctx.fetch_scope_mode())

    # 2. check type of body
    for instr in ewith.body:
        if not instr.type_check(ctx):
            ctx.pop_parent()
            return False

    # pop the parent and repush
    ctx.pop_parent()

    return True

With.type_check = type_check_With

def ContainerAssign_type_check(cassign, ctx):
    container_type = cassign.container_expr.type_infer(ctx)
    if container_type is None:
        return False

    if isinstance(container_type, DictType):
        if container_type.key_type is None:
            ctx.add_type_error(ContainerAssignEmptyError(cassign))
            return False
        key_type = container_type.key_type
        val_type = container_type.val_type
    elif isinstance(container_type, ListType):
        key_type = IntType()
        val_type = container_type.elem_type
    else:
        ctx.add_type_error(ContainerAssignTypeError(cassign, container_type))
        return False

    if not type_expect(ctx, cassign.container_index, key_type, raise_error=True):
        return False

    if not type_expect(ctx, cassign.assign_expr, val_type, raise_error=True):
        return False

    (has_side_effect, protected_var) = cassign.side_effect(container_type, ctx)
    if has_side_effect and not ctx.function_def.procedure:
        ctx.add_type_error(SideEffectContainerWarning(ctx.function_def,cassign,"assign", cassign.container_expr, protected_var))

    return True

ContainerAssign.type_check = ContainerAssign_type_check

######################################
# Type inference                     #
######################################

def type_infer_UnsupportedNode(node, ctx):
    #print("Error: Type inference for unsupported node")
    #import astpp
    #print(astpp.dump(node.ast))
    ctx.add_type_error(UnsupportedNodeError(node))

    return None


UnsupportedNode.type_infer = type_infer_UnsupportedNode


def infer_number_type(ctx, type1, type2):
    # float always "wins"
    if isinstance(type1, FloatType):
        return type1
    if isinstance(type2, FloatType):
        return type2
    # otherwise Number wins
    if isinstance(type1, NumberType):
        return type1
    if isinstance(type2, NumberType):
        return type2

    # otherwise it's either of the two (an int, guessing ...)
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


        if left_type.elem_type is not None and right_type.elem_type is not None and left_type.elem_type != right_type.elem_type:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, left_type.elem_type, expr.right, right_type.elem_type,
                                                   tr("Expecting a list with elements of type: {}").format(left_type.elem_type)))
            return None

        if left_type.elem_type is None and right_type.elem_type is not None:
            return right_type
        else:
            return left_type

    else:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, ListType(), expr.left, left_type,
                                               tr("Expecting a list")))
        return None

EAdd.type_infer = type_infer_EAdd

def type_infer_ESub(expr, ctx):
    left_type = expr.left.type_infer(ctx)
    if left_type is None:
        return None

    if isinstance(left_type, SetType):
        # for sets

        right_type = expr.right.type_infer(ctx)
        if not right_type:
            return None

        if not isinstance(right_type, SetType):
            ctx.add_type_error(TypeExpectationError(ctx.function_def, expr.right, right_type, tr("Expecting a set")))
            return None

        if left_type.is_emptyset():
            return right_type

        if right_type.is_emptyset():
            return left_type

        right_type = type_expect(ctx, expr.right, left_type)
        if not right_type:
            return None

        return left_type


    # for numbers

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
    left_type = expr.left.type_infer(ctx)
    if not left_type:
        return None

    # first case if the left operand is a string, a liste or a sequence

    if isinstance(left_type, (StrType, ListType, SequenceType)):
        right_type = type_expect(ctx, expr.right, IntType())
        if not right_type:
            return None
        else:
            return left_type

    # second case if the left operand is an int, and the right operand is a str, sequence or list
    if isinstance(left_type, IntType):
        right_type = expr.right.type_infer(ctx)
        if not right_type:
            return None
        if isinstance(right_type, (StrType, ListType, SequenceType)):
            # in python : return right_type
            ctx.add_type_error(UnsupportedNodeError(expr))
            return None

    # default case : the normal multiplication for numbers

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
    left_type = type_expect(ctx, expr.left, NumberType())
    if not left_type:
        return None

    right_type = type_expect(ctx, expr.right, NumberType())
    if not right_type:
        return None

    pow_type = infer_number_type(ctx, left_type, right_type)
    if not pow_type:
        return None

    return pow_type

EPow.type_infer = type_infer_EPow

def type_infer_EBitOr(expr, ctx):
    left_type = expr.left.type_infer(ctx)
    if not left_type:
        return None

    if not isinstance(left_type, SetType):
        ctx.add_type_error(TypeExpectationError(ctx.function_def, expr.left, left_type, tr("Expecting a set")))
        return None

    right_type = expr.right.type_infer(ctx)
    if not right_type:
        return None

    if not isinstance(right_type, SetType):
        ctx.add_type_error(TypeExpectationError(ctx.function_def, expr.right, right_type, tr("Expecting a set")))
        return None

    if left_type.is_emptyset():
        return right_type

    if right_type.is_emptyset():
        return left_type

    right_type = type_expect(ctx, expr.right, left_type)
    if not right_type:
        return None

    return left_type

EBitOr.type_infer = type_infer_EBitOr

def type_infer_EBitAnd(expr, ctx):
    left_type = expr.left.type_infer(ctx)
    if not left_type:
        return None

    if not isinstance(left_type, SetType):
        ctx.add_type_error(TypeExpectationError(ctx.function_def, expr.left, left_type, tr("Expecting a set")))
        return None

    right_type = expr.right.type_infer(ctx)
    if not right_type:
        return None

    if not isinstance(right_type, SetType):
        ctx.add_type_error(TypeExpectationError(ctx.function_def, expr.right, right_type, tr("Expecting a set")))
        return None

    if left_type.is_emptyset():
        return right_type

    if right_type.is_emptyset():
        return left_type

    right_type = type_expect(ctx, expr.right, left_type)
    if not right_type:
        return None

    return left_type

EBitAnd.type_infer = type_infer_EBitAnd

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

    # or maybe the variable is a global function (HOF)
    if var.name in ctx.global_env:
        return ctx.global_env[var.name]

    # or, is it a global variable ?
    for global_var in ctx.prog.global_vars:
        if isinstance(global_var, DeclareVar) and isinstance(global_var.target, LHSVar):
            if var.name == global_var.target.var_name:
                ctx.add_type_error(GlobalVariableUseError(var.name, var))
                return None

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


def type_infer_EMin(node, ctx):
    return type_infer_narynum(node.args, ctx)

EMin.type_infer = type_infer_EMin

def type_infer_EMax(node, ctx):
    return type_infer_narynum(node.args, ctx)

EMax.type_infer = type_infer_EMax

def type_infer_narynum(args, ctx):
    targ = None
    only_ints = True
    for arg in args:
        targ = arg.type_infer(ctx)
        if not targ:
            return None
        if not isinstance(targ, (NumberType, FloatType, IntType)):
            ctx.add_type_error(NaryNumOpArgNotNumeric(arg))
            return None
        if not isinstance(targ, IntType):
            only_ints = False
    if only_ints:
        return IntType()
    else:
        return FloatType()

ENone.type_infer = type_infer_ENone

def type_infer_ECall(call, ctx):
    # step 1 : fetch the signature of the called function
    if call.full_fun_name in ctx.global_env:
        method_call = False
        hof_call = False
        signature = ctx.global_env[call.full_fun_name]
        arguments = call.arguments
    elif "." + call.fun_name in { ".append", ".readlines", ".read", ".write", ".add", ".remove", ".items", ".keys" }: #XXX: needed ? and not call.multi_receivers:
        method_call = True
        hof_call = False
        signature = ctx.global_env["." + call.fun_name]
        arguments = []
        arguments.append(call.receiver)
        arguments.extend(call.arguments)
    elif ctx.function_def and call.full_fun_name in ctx.function_def.parameters:
        # handling of HOF
        hof_call = True
        method_call = False
        param_idx = ctx.function_def.parameters.index(call.full_fun_name)
        signature = ctx.global_env[ctx.function_def.name].param_types[param_idx]
        arguments = call.arguments
    else:
        ctx.add_type_error(UnknownFunctionError(ctx.function_def, call))
        return None

    # step 1bis : we rename the type parameters to avoid any nameclash
    rename_map = {}
    if not hof_call:
        signature = signature.rename_type_variables(rename_map)
    #print("rename_map = {}".format(rename_map))
    #print(repr(signature))

    # step 2 : check the call arity (only if TypeAnything is not present)
    check_arity = True
    for param_type in signature.param_types:
        if isinstance(param_type, Anything):
            check_arity = False

    if check_arity and (len(signature.param_types) != len(arguments)):
        ctx.add_type_error(CallArityError(method_call, signature.param_types, arguments, call))
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
    else:
        nret_type = signature.ret_type

    ctx.call_type_env.pop()

    # check if there is an unhashable set or dict
    unhashable = nret_type.fetch_unhashable()
    if unhashable is not None:
        if isinstance(unhashable, SetType):
            ctx.add_type_error(UnhashableElementError(call, call, unhashable.elem_type))
            return None
        elif isinstance(unhashable, DictType):
            ctx.add_type_error(UnhashableKeyError(call, call, unhashable.key_type))
            return None

    (has_side_effect, protected_var) = call.side_effect(ctx)
    if has_side_effect and not ctx.function_def.procedure:
        ctx.add_type_error(SideEffectWarning(ctx.function_def,call,call.fun_name, call.receiver, protected_var))

    return nret_type

ECall.type_infer = type_infer_ECall


def type_infer_ERange(erange, ctx):
    if erange.start is None and erange.stop is None:
        ctx.add_type_error(ERangeArgumentError(erange))
        return None

    if erange.start is not None:
        start_type = type_expect(ctx, erange.start, IntType())
        if start_type is None:
            return None

    stop_type = type_expect(ctx, erange.stop, IntType())
    if stop_type is None:
        return None

    if erange.step:
        if type_expect(ctx, erange.step, IntType()) is None:
            return None

    return SequenceType(IntType())

ERange.type_infer = type_infer_ERange

def type_infer_ECompare(ecomp, ctx):
    for cond in ecomp.conds:
        if not cond.type_check(ctx, ecomp):
            return None

    return BoolType()

ECompare.type_infer = type_infer_ECompare

def type_check_Condition(cond, ctx, compare):

    if isinstance(cond, (CEq, CNotEq, CLt, CLtE, CGt, CGtE)):
        left_right_ok = False

        left_type = cond.left.type_infer(ctx)

        if left_type is None:
            return False

        # HACK : will see if a warning is raised
        nb_errors = len(ctx.type_errors)

        if type_expect(ctx, cond.right, left_type, raise_error=False) is not None:
            left_right_ok = True

        right_type = cond.right.type_infer(ctx)
        if right_type is None:
            return False

        if left_right_ok:
            return True
        elif ((type_expect(ctx, cond.left, right_type, raise_error=False) is None)
              #and (type_expect(ctx, cond.right, left_type, raise_error=False) is None)
        ):
            ctx.add_type_error(CompareConditionError(compare, cond, left_type, right_type))
            return False


        return True

    elif isinstance(cond, (CIn, CNotIn)):

        container_type = cond.right.type_infer(ctx)
        if container_type is None:
            return False

        if isinstance(container_type, SetType):
            set_type = container_type

            if set_type.elem_type is None:
                return True # XXX: the emptyset is compatible with everything

            if type_expect(ctx, cond.left, set_type.elem_type) is None:
                return False

            return True

        elif isinstance(container_type, DictType):
            dict_type = container_type

            if dict_type.key_type is None:
                return True # XXX : the emptydict is compatible with everything

            if type_expect(ctx, cond.left, dict_type.key_type) is None:
                return False

            return True

        else:
            ctx.add_type_error(MembershipTypeError(cond.right, container_type))
            return False

    else:
        raise ValueError("Condition not supported (please report): {}".format(cond))


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
            if (isinstance(lst_type, (IntType, FloatType, NumberType))
                and isinstance(element_type, (IntType, FloatType, NumberType))):
                lst_type = infer_number_type(ctx, lst_type, element_type)
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
        result_type = subject_type.val_type
    else:
        ctx.add_type_error(IndexingError(indexing, subject_type))
        return None

    if sequential:
        if type_expect(ctx, indexing.index, IntType(), raise_error=False) is None:
            ctx.add_type_error(IndexingSequenceNotNumeric(indexing.index))
            return None
    else: # dictionary

        if type_expect(ctx, indexing.index, subject_type.key_type, raise_error=False) is None:
            ctx.add_type_error(IndexingDictKeyTypeError(indexing.index, subject_type.key_type))
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

def type_infer_EComp(ecomp, ctx):
    # we will modify the lexical environment
    ctx.push_parent(ecomp)

    for generator in ecomp.generators:
        # fetch the type of the iterator expr
        iter_type = generator.iter.type_infer(ctx)
        if iter_type is None:
            ctx.pop_parent()
            return None

        if isinstance(iter_type, (IterableType, SequenceType, ListType, SetType, StrType, DictType)):
            iter_elem_type = None
            if isinstance(iter_type, StrType):
                iter_elem_type = StrType() # XXX: ugly language trait
            elif isinstance(iter_type, DictType):
                iter_elem_type = iter_type.key_type
            else:
                iter_elem_type = iter_type.elem_type

            # if generator.target.arity() == 1:
            #     var = generator.target.variables()[0]
            #     if var.var_name in ctx.dead_variables:
            #         ctx.add_type_error(DeadVariableDefineError(var.var_name, var))
            #         ctx.pop_parent()
            #         return None
            #     elif var.var_name in ctx.local_env:
            #         ctx.add_type_error(IterVariableInEnvError(var.var_name, var))
            #         ctx.pop_parent()
            #         return None
            #     # check that the variable is not a parameter
            #     elif ctx.param_env and var.var_name in ctx.param_env:
            #         ctx.add_type_error(ParameterInCompError(var.var_name, var))
            #         return None
            #     elif var.var_name != "_":
            #         ctx.local_env[var.var_name] = (iter_elem_type, ctx.fetch_scope_mode())
            # else: # tuple destruct
            #     if not isinstance(iter_elem_type, TupleType):
            #         ctx.add_type_error(TypeExpectationError(ctx.function_def, generator.iter, iter_elem_type,
            #                                                 tr("Expecting an iterator of tuples")))
            #         ctx.pop_parent()
            #         return None

                # expr_var_types = check_linearized_tuple_type(iter_elem_type)

                # if len(expr_var_types) != len(generator.target.variables()):
                #     ctx.add_type_error(TupleDestructArityError(generator.target, iter_elem_type, len(expr_var_types), len(generator.target.variables())))
                #     ctx.pop_parent()
                #     return None

            declared_types = dict()

            for (i, var) in zip(range(0, len(generator.target.variables())), generator.target.variables()):
                if var.var_name in ctx.dead_variables:
                    ctx.add_type_error(DeadVariableDefineError(var.var_name, var))
                    ctx.pop_parent()
                    return None
                # check that the variable is not a parameter
                elif ctx.param_env and var.var_name in ctx.param_env:
                    ctx.add_type_error(ParameterInCompError(var.var_name, var))
                    return None
                elif var.var_name in ctx.local_env:
                    ctx.add_type_error(IterVariableInEnvError(var.var_name, var))
                    ctx.pop_parent()
                    return None
                elif var.var_name in ctx.declared_env:
                    declared_types[var.var_name] = ctx.declared_env[var.var_name][0]

            # now the lexical env is built for this generator conditions

            if not check_linearized_tuple_type(generator.target, iter_elem_type, declared_types, ctx, generator.target):
                ctx.pop_parent(protected_vars={v for v in declared_types})
                return None

            for condition in generator.conditions:
                if not type_expect(ctx, condition, BoolType()):
                    ctx.pop_parent()
                    return None

        else:
            ctx.add_type_error(IteratorTypeError(for_node, iter_type))
            ctx.pop_parent()
            return None

    # once all generators have been type checked

    if isinstance(ecomp, EDictComp):
        key_type = ecomp.key_expr.type_infer(ctx)
        if key_type is None:
            ctx.pop_parent()
            return None

        val_type = ecomp.val_expr.type_infer(ctx)
        if val_type is None:
            ctx.pop_parent()
            return None

    else: # list or set
        expr_type = ecomp.compr_expr.type_infer(ctx)
        if expr_type is None:
            ctx.pop_parent()
            return None

    ctx.pop_parent()

    if isinstance(ecomp, EListComp):
        return ListType(expr_type)
    elif isinstance(ecomp, ESetComp):
        if not expr_type.is_hashable():
            ctx.add_type_error(UnhashableElementError(ecomp, ecomp.compr_expr, expr_type))
            return None

        return SetType(expr_type)
    elif isinstance(ecomp, EDictComp):
        if not key_type.is_hashable():
            ctx.add_type_error(UnhashableKeyError(ecomp, ecomp.key_expr, key_type))
            return None
        return DictType(key_type, val_type)
    else:
        raise ValueError("Comprehension not supported: {} (please report)".format(ecomp))

EListComp.type_infer = type_infer_EComp
ESetComp.type_infer = type_infer_EComp
EDictComp.type_infer = type_infer_EComp

def type_infer_ESet(st, ctx):
    st_type = None
    if not st.elements:
        return SetType()

    for element in st.elements:
        element_type = element.type_infer(ctx)
        if element_type is None:
            return None
        #print("----\nelement type={}".format(element_type))
        #print("st type={}\n----".format(st_type))

        if not element_type.is_hashable():
            ctx.add_type_error(UnhashableElementError(st, element, element_type))
            return None

        if st_type is None:
            st_type = element_type
        else:
            if (isinstance(st_type, (IntType, FloatType, NumberType))
                and isinstance(element_type, (IntType, FloatType, NumberType))):
                st_type = infer_number_type(ctx, st_type, element_type)
            else:
                if not st_type.type_compare(ctx, element, element_type, raise_error=False):
                    ctx.add_type_error(HeterogeneousElementError('set', st, st_type, element_type, element))
                    return None

    return SetType(st_type)

ESet.type_infer = type_infer_ESet

def type_infer_EDict(edict, ctx):
    if not edict.keys:
        return DictType()

    # key type
    edict_key_type = None
    for key in edict.keys:
        key_type = key.type_infer(ctx)
        if key_type is None:
            return None

        if not key_type.is_hashable():
            ctx.add_type_error(UnhashableKeyError(edict, key, key_type))
            return None

        if edict_key_type is None:
            edict_key_type = key_type
        else:
            if (isinstance(edict_key_type, (IntType, FloatType, NumberType))
                and isinstance(key_type, (IntType, FloatType, NumberType))):
                edict_key_type = infer_number_type(ctx, edict_key_type, key_type)
            else:
                if not edict_key_type.type_compare(ctx, key, key_type, raise_error=False):
                    ctx.add_type_error(HeterogeneousElementError('set', edict, edict_key_type, key_type, key))
                    return None

    # value type
    edict_val_type = None

    for val in edict.values:
        val_type = val.type_infer(ctx)
        if val_type is None:
            return None

        if edict_val_type is None:
            edict_val_type = val_type
        else:
            if (isinstance(edict_val_type, (IntType, FloatType, NumberType))
                and isinstance(val_type, (IntType, FloatType, NumberType))):
                edict_val_type = infer_number_type(ctx, edict_val_type, val_type)
            else:
                if not edict_val_type.type_compare(ctx, val, val_type, raise_error=False):
                    ctx.add_type_error(HeterogeneousElementError('dictionary', edict, edict_val_type, val_type, key))
                    return None

    return DictType(edict_key_type, edict_val_type)

EDict.type_infer = type_infer_EDict

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

def type_compare_FunctionType(expected_type, ctx, expr, expr_type, raise_error=True):
    if not isinstance(expr_type, FunctionType):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Function")))

        return False

    expected_param_types = expected_type.param_types
    expr_param_types = expr_type.param_types
    if len(expected_param_types) != len(expr_param_types):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Wrong arity")))
        return False


    for (expected_param_type, expr_param_type) in zip(expected_param_types, expr_param_types):
        if not expected_param_type.type_compare(ctx, expr, expr_param_type, raise_error):
            if raise_error:
                ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Error for function parameter")))
            return False

    if not expected_type.ret_type.type_compare(ctx, expr, expr_type.ret_type, raise_error):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Error for function return type")))
        return False

    return True

FunctionType.type_compare = type_compare_FunctionType

def check_option_type(cause_fn, expected_precise_type, ctx, expr, expr_option_type, raise_error=True):
    # precondition 1: expected type is not an option type
    # precondition 2: expr_type is an option type
    ok = cause_fn(expected_precise_type, ctx, expr, expr_option_type.elem_type, raise_error)
    if ok:
        ctx.add_type_error(OptionCoercionWarning(expr, expr_option_type, expected_precise_type))
        # in any case there is no error
        return True
    else:
        return False

def type_compare_NumberType(expected_type, ctx, expr, expr_type, raise_error=True):
    # XXX: boilerplate ... could use a decorator of some sort ?
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_NumberType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, NumberType) \
       or isinstance(expr_type, IntType) \
       or isinstance(expr_type, FloatType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Number")))

    return False

NumberType.type_compare = type_compare_NumberType

def type_compare_IntType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_IntType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, IntType):
        return True

    if isinstance(expr_type, NumberType):
        if raise_error:
            ctx.add_type_error(TypeImprecisionWarning(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an int")))
        # the comparision is imprecise, but there's no failure
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an int")))

    return False

IntType.type_compare = type_compare_IntType

def type_compare_FloatType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_FloatType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, (FloatType, IntType, NumberType)):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a float")))

    return False

FloatType.type_compare = type_compare_FloatType

def type_compare_BoolType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_BoolType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, BoolType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a Bool (type bool)")))

    return False

BoolType.type_compare = type_compare_BoolType

def type_compare_FileType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, FileType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a File")))

    return False

FileType.type_compare = type_compare_FileType

def type_compare_ImageType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_ImageType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, ImageType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an image (type Image)")))

    return False

ImageType.type_compare = type_compare_ImageType

def type_compare_StrType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_StrType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, StrType):
        return True

    if raise_error:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a string (type str)")))

    return False

StrType.type_compare = type_compare_StrType

def type_compare_ListType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_ListType, expected_type, ctx, expr, expr_type, raise_error)

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

def type_compare_SetType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_SetType, expected_type, ctx, expr, expr_type, raise_error)

    if not isinstance(expr_type, SetType):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a set")))
        return False

    if expr_type.is_emptyset():
        return True

    if expected_type.is_emptyset():
        return True

    return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

SetType.type_compare = type_compare_SetType

def type_compare_IterableType(expected_type, ctx, expr, expr_type, raise_error=True):
    
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_IterableType, expected_type, ctx, expr, expr_type, raise_error)

    if isinstance(expr_type, ListType) and expr_type.is_emptylist():
        return True

    if isinstance(expr_type, SetType) and expr_type.is_emptyset():
        return True

    if isinstance(expr_type, IterableType) \
       or isinstance(expr_type, SequenceType) \
       or isinstance(expr_type, ListType) \
       or isinstance(expr_type, SetType):
        return expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error)

    elif isinstance(expr_type, StrType):
        return expected_type.elem_type.type_compare(ctx, expr, StrType(), raise_error)

    elif isinstance(expr_type, DictType):
        return expected_type.elem_type.type_compare(ctx, expr, expr_type.key_type, raise_error)
    else:
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an Iterable (Sequence, list, string, set or dictionnary)")))
        return False

IterableType.type_compare = type_compare_IterableType

def type_compare_SequenceType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_SequenceType, expected_type, ctx, expr, expr_type, raise_error)

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

    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_TypeVariable, expected_type, ctx, expr, expr_type, raise_error)

    # some corner case handled here ...
    if expected_type == expr_type:
        return True

    if expected_type.is_call_variable() and len(ctx.call_type_env) > 0: # XXX: the right test is a little bit "fishy"...
        if expected_type.var_name in ctx.call_type_env[-1]:
            real_expected_type = ctx.call_type_env[-1][expected_type.var_name]

            if not isinstance(real_expected_type, TypeVariable):
                if not real_expected_type.type_compare(ctx, expr, expr_type, raise_error=False):
                    ctx.add_type_error(TypeComparisonError(ctx.function_def, real_expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:],real_expected_type, expr_type)))
                    return False
                else:
                    return True

            # XXX: strange corner case (to check ...)
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
        # XXX: is it always safe to accept the comparison ?
        # or an error should be returned
        return True
        
        # if raise_error:
        #     ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Type mismatch for parameter #{} in call, expecting {} found: {}").format(expected_type.var_name[1:], expected_type, expr_type)))
        # return False

TypeVariable.type_compare = type_compare_TypeVariable

def type_compare_NoneTypeType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_NoneTypeType, expected_type, ctx, expr, expr_type, raise_error)

    if not isinstance(expr_type, NoneTypeType):
        if raise_error:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting value None")))
        return False

    return True

NoneTypeType.type_compare = type_compare_NoneTypeType

def type_compare_OptionType(expected_type, ctx, expr, expr_type, raise_error=True):

    # expression type is an option
    if isinstance(expr_type, OptionType):
        val_type = expected_type.elem_type.type_compare(ctx, expr, expr_type.elem_type, raise_error=False)
        if not val_type:
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type.elem_type, expr, expr_type.elem_type, tr("Expecting value of type: {}").format(expected_type)))
            return False
        else:
            return True

    # expression type is not an option type

    if isinstance(expr_type, NoneTypeType):
        return True

    val_type = expected_type.elem_type.type_compare(ctx, expr, expr_type, raise_error=False)
    if not val_type:
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting value None or of type: {}").format(expected_type.elem_type)))
        return False

    return True

OptionType.type_compare = type_compare_OptionType

def type_compare_TupleType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_TupleType, expected_type, ctx, expr, expr_type, raise_error)

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

def type_compare_DictType(expected_type, ctx, expr, expr_type, raise_error=True):
    if isinstance(expr_type, OptionType):
        return check_option_type(type_compare_DictType, expected_type, ctx, expr, expr_type, raise_error)

    if not isinstance(expr_type, DictType):
        ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting a dictionary")))
        return False

    if expr_type.is_emptydict():
        return True # the empty dictionary is compatible with all dictionaries

    if expected_type.is_emptydict():
        if not expr_type.is_emptydict():
            ctx.add_type_error(TypeComparisonError(ctx.function_def, expected_type, expr, expr_type, tr("Expecting an empty dictionary")))
            return False
        else: # both empty
            return True

    if not expected_type.key_type.type_compare(ctx, expr, expr_type.key_type, raise_error):
        return False

    if not expected_type.val_type.type_compare(ctx, expr, expr_type.val_type, raise_error):
        return False

    return True

DictType.type_compare = type_compare_DictType

######################################
# Standard imports                   #
######################################

BUILTINS_IMPORTS = {
    'len' : FunctionType([IterableType(TypeVariable('α'))], IntType())
    ,'abs' : FunctionType([FloatType()], FloatType())
    ,'print' : FunctionType([Anything()], NoneTypeType())
    ,'min' : FunctionType([FloatType(), FloatType()], FloatType())
    ,'max' : FunctionType([FloatType(), FloatType()], FloatType())
    # ,'range' : function_type_parser("int * int -> Iterable[int]").content  # range is an expression now
    , 'int' : FunctionType([Anything()], IntType())
    , 'float' : FunctionType([Anything()], FloatType())
    , 'str' : FunctionType([Anything()], StrType())
    , 'ord' : FunctionType([StrType()], IntType())
    , 'chr' : FunctionType([IntType()], StrType())
    , 'round' : FunctionType([NumberType()], IntType())
    , '.append' : FunctionType([ListType(TypeVariable('α')),TypeVariable('α')], NoneTypeType())
    # images   ... TODO: the type system is not precise enough (for now)
    , 'draw_line' :  FunctionType([FloatType(), FloatType(), FloatType(), FloatType(), Anything()], ImageType())
    , 'overlay' : FunctionType([ImageType(), ImageType(), Anything()], ImageType())
    , 'underlay' : FunctionType([ImageType(), ImageType(), Anything()], ImageType())
    , 'fill_triangle' : FunctionType([FloatType(), FloatType(), FloatType(), FloatType(), FloatType(),FloatType(), Anything()], ImageType())
    , 'draw_triangle' : FunctionType([FloatType(), FloatType(), FloatType(), FloatType(), FloatType(),FloatType(), Anything()], ImageType())
    , 'draw_ellipse' : FunctionType([FloatType(), FloatType(), FloatType(), FloatType(), Anything()], ImageType())
    , 'fill_ellipse' : FunctionType([FloatType(), FloatType(), FloatType(), FloatType(), Anything()], ImageType())
    , 'show_image' : FunctionType([ImageType()], NoneTypeType())
    # fichiers
    , 'open' : FunctionType([StrType(),StrType()], FileType())
    , '.readlines' : FunctionType([FileType()], ListType(StrType()))
    , '.read' : FunctionType([FileType()], StrType())
    , '.write' : FunctionType([FileType(),StrType()], NoneTypeType())
    # ensembles
    , 'set' : FunctionType([], SetType())
    , '.add' : FunctionType([SetType(TypeVariable('α')),TypeVariable('α')], NoneTypeType())
    , '.remove' : FunctionType([SetType(TypeVariable('α')),TypeVariable('α')], NoneTypeType())
    # dictionnaires
    , 'dict' : FunctionType([], DictType())
    , '.items' : FunctionType([DictType(key_type = TypeVariable('α'),val_type = TypeVariable('β'))], IterableType(TupleType([TypeVariable('α'),TypeVariable('β')])))
    , '.keys' : FunctionType([DictType(TypeVariable('α'),TypeVariable('β'))], SetType(TypeVariable('α')))
    # iterables
    , 'zip' :  FunctionType([IterableType(TypeVariable('α')),IterableType(TypeVariable('β'))], IterableType(TupleType([TypeVariable('α'),TypeVariable('β')])))
}

MATH_IMPORTS = {
    'math.sqrt' : FunctionType([FloatType()], FloatType())
    , 'math.floor' : FunctionType([FloatType()], IntType())
    , 'math.ceil' : FunctionType([FloatType()], IntType())
    , 'math.sin' : FunctionType([FloatType()], FloatType())
    , 'math.cos' : FunctionType([FloatType()], FloatType())
    , 'math.tan' : FunctionType([FloatType()], FloatType())
    , 'math.cosh' : FunctionType([FloatType()], FloatType())
    , 'math.sinh' : FunctionType([FloatType()], FloatType())
    , 'math.tanh' : FunctionType([FloatType()], FloatType())
    , 'math.acos' : FunctionType([FloatType()], FloatType())
    , 'math.asin' : FunctionType([FloatType()], FloatType())
    , 'math.atan' : FunctionType([FloatType()], FloatType())
    , 'math.acosh' : FunctionType([FloatType()], FloatType())
    , 'math.asinh' : FunctionType([FloatType()], FloatType())
    , 'math.atanh' : FunctionType([FloatType()], FloatType())
    , 'math.factorial' : FunctionType([IntType()], IntType())
    , 'math.log' : FunctionType([FloatType()], FloatType())
    }


RANDOM_IMPORTS = {
    'random.random' : FunctionType([], FloatType())
    , 'random.seed' : FunctionType([IntType()], NoneTypeType())
}

REGISTERED_IMPORTS = {
    '' : BUILTINS_IMPORTS
    , 'math' : MATH_IMPORTS
    , 'random' : RANDOM_IMPORTS
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
        report.add_convention_error('error', tr("Signature problem"), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , details=tr("I don't understand the signature of function '{}'").format(self.fun_name))

    def is_fatal(self):
        return False

class SignatureTrailingError(TypeError):
    def __init__(self, fun_name, fun_def, remaining):
        self.fun_name = fun_name
        self.fun_def = fun_def
        self.trailing = ""
        while remaining and not remaining[0].isspace():
            self.trailing += remaining[0]
            remaining = remaining[1:]

    def fail_string(self):
        return "SignatureTrailingError[{}/{}]@{}:{}".format(self.fun_name, self.trailing, self.fun_def.ast.lineno, self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Signature problem"), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , details=tr("The signature of function '{}' contains some characters at the end that I do not understand: {}").format(self.fun_name, self.trailing))

    def is_fatal(self):
        return False

class TypeDefParseError(TypeError):
    def __init__(self, lineno, type_name):
        self.lineno = lineno
        self.type_name = type_name

    def fail_string(self):
        return "TypeDefParseError[{}]@{}:{}".format(self.type_name, self.lineno, 0)

    def report(self, report):
        report.add_convention_error('error', tr("Type expression problem"), self.lineno, 0
                                    , details="{}".format(self.type_name))

    def is_fatal(self):
        return False

class TypeExprParseError(TypeError):
    def __init__(self, lineno, col_offset, message):
        self.lineno = lineno
        self.col_offset = col_offset
        self.message = message

    def fail_string(self):
        return "TypeExprParseError[{}]@{}:{}".format(self.message, self.lineno, self.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Type expression problem"), self.lineno, self.col_offset
                                    , details=self.message)

    def is_fatal(self):
        return True

class DuplicateTypeDefError(TypeError):
    def __init__(self, lineno, type_name):
        self.lineno = lineno
        self.type_name = type_name

    def fail_string(self):
        return "DuplicateTypeDefError[{}]@{}:{}".format(self.type_name, self.lineno, 0)

    def report(self, report):
        report.add_convention_error('error', tr("Type definition problem"), self.lineno, 0
                                    , details=tr("There is already a definition for type '{}'").format(self.type_name))

    def is_fatal(self):
        return False

class DuplicateMultiAssignError(TypeError):
    def __init__(self, lineno, var_name):
        self.lineno = lineno
        self.var_name = var_name

    def fail_string(self):
        return "DuplicateMultiAssignError[{}]@{}:{}".format(self.var_name, self.lineno, 0)

    def report(self, report):
        report.add_convention_error('error', tr("Declaration problem"), self.lineno, 0
                                    , details=tr("Variable '{}' was declared multiple times").format(self.var_name))

    def is_fatal(self):
        return True

class DuplicateMultiFunDeclarationError(TypeError):
    def __init__(self, lineno, fun_name):
        self.lineno = lineno
        self.fun_name = fun_name

    def fail_string(self):
        return "DuplicateMultiFunDeclarationError[{}]@{}:{}".format(self.fun_name, self.lineno, 0)

    def report(self, report):
        report.add_convention_error('error', tr("Function definition problem"), self.lineno, 0
                                    , details=tr("Function '{}' was defined multiple times").format(self.fun_name))

    def is_fatal(self):
        return True



class AssertionInFunctionWarning(TypeError):
    def __init__(self, fun_name, assertion):
        self.fun_name = fun_name
        self.assertion = assertion

    def fail_string(self):
        return "AssertionInFunctionWarning[{}]@{}:{}".format(self.fun_name, self.assertion.ast.lineno, self.assertion.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Assertion issue"), self.assertion.ast.lineno, self.assertion.ast.col_offset
                                    , details=tr("In Python101 the `asserts` are reserved for test cases, however one assert is present in the body of function '{}'").format(self.fun_name))

    def is_fatal(self):
        return False

class NotUsedDeclarationWarning(TypeError):
    def __init__(self, fun_def, var_name, var_info):
        self.fun_def = fun_def
        self.var_name = var_name
        self.var_type, self.var_info = var_info

    def fail_string(self):
        return "NotUsedDeclarationWarning[{}]@{}:{}".format(self.var_name, self.var_info['lineno'], self.var_info['col_offset'])

    def report(self, report):
        report.add_convention_error('warning', tr("Unused variable"), self.var_info['lineno'], self.var_info['col_offset'], details=tr("The variable '{}' is declared but not used").format(self.var_name))

    def is_fatal(self):
        return False

class DifferentDeclarationWarning(TypeError):
    def __init__(self,lineno, var_name):
        self.var_name = var_name
        self.lineno = lineno

    def fail_string(self):
        return "DifferentDeclarationWarning[{}]@{}:{}".format(self.var_name, self.var_type)

    def report(self, report):
        report.add_convention_error('warning', tr("Declaration problem"), self.lineno, 0
                                    , details=tr("Warning you've initialzed in 2 differents ways the variable: '{}'").format(self.var_name))

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


class FunctionUnhashableError(TypeError):
    def __init__(self, func_def, unhashable_type):
        self.func_def = func_def
        self.unhashable_type = unhashable_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "FunctionUnhashableError[{}:{}]@{}:{}".format(self.func_def.name
                                                             , self.unhashable_type
                                                             , self.func_def.ast.lineno
                                                             , self.func_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Type declaration error"), self.func_def.ast.lineno, self.func_def.ast.col_offset
                                    , tr("Wrong use in signature of function '{}' of mutable (not hashable) type: {}").format(self.func_def.name, self.unhashable_type))


class UnsupportedNodeError(TypeError):
    def __init__(self, node):
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnsupportedNodeError[{}]@{}:{}".format(str(self.node.ast.__class__.__name__)
                                                       , self.node.ast.lineno
                                                       , self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Not-Python101'), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("this construction is not available in Python101 (try expert mode for standard Python)"))

class UnsupportedElseError(TypeError):
    def __init__(self, node):
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnsupportedElseError[{}]@{}:{}".format(str(self.node.ast.__class__.__name__)
                                                       , self.node.ast.lineno
                                                       , self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Not-Python101'), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Loops with `else` clause not supported"))

class UnsupportedTopLevelNodeError(TypeError):
    def __init__(self, node):
        self.node = node

    def is_fatal(self):
        return False

    def fail_string(self):
        return "UnsupportedTopLevelNodeError[{}]@{}:{}".format(str(self.node.ast.__class__.__name__)
                                                       , self.node.ast.lineno
                                                       , self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Wrong statement'), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("In Python 101 this statement cannot be done outside a function body (try expert mode for standard Python)"))

class WrongFunctionDefError(TypeError):
    def __init__(self, fun_def):
        self.fun_def = fun_def

    def is_fatal(self):
        return False

    def fail_string(self):
        return "WrongFunctionDefError[{}]@{}:{}".format(str(self.fun_def.ast.name)
                                                        , self.fun_def.ast.lineno
                                                        , self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr('Wrong definition'), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , tr("The function '{}' has no correct specification.").format(self.fun_def.ast.name))
    
class FunctionPreconditionWarning(TypeError):
    def __init__(self, fun_def, precondition_type, lineno):
        self.fun_def = fun_def
        self.precondition_type = precondition_type
        self.lineno = lineno

    def is_fatal(self):
        return False

    def fail_string(self):
        return "FunctionPreconditionWarning[{}]@{}:{}".format(str(self.fun_def.ast.name)
                                                        , self.lineno
                                                        , self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr('Wrong definition'), self.lineno, self.fun_def.ast.col_offset
                                    , tr("The precondition in '{}' should be a 'bool', not a '{}'.").format(self.fun_def.ast.name, self.precondition_type))

class UndefinedVarInPreconditionWarning(TypeError):
    def __init__(self, fun_def, var, lineno):
        self.fun_def = fun_def
        self.var = var
        self.lineno = lineno

    def is_fatal(self):
        return False

    def fail_string(self):
        return "UndefinedVarInPreconditionWarning[{} in {}]@{}:{}".format(self.var.name,str(self.fun_def.ast.name),self.lineno, self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Undefined variable"), self.lineno, self.fun_def.ast.col_offset
                                    , details=tr("The variable '{}' in the precondition is undefined.").format(self.var.name))

class ErrorInPreconditionWarning(TypeError):
    def __init__(self, fun_def, lineno):
        self.fun_def = fun_def
        self.lineno = lineno

    def is_fatal(self):
        return False

    def fail_string(self):
        return "ErrorInPreconditionWarning[in {}]@{}:{}".format(str(self.fun_def.ast.name),self.lineno, self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Syntax error"), self.lineno, self.fun_def.ast.col_offset
                                    , details=tr("There is an error in the function '{}' precondition.").format(self.fun_def.name))


class NoFunctionDocWarning(TypeError):
    def __init__(self, fun_def):
        self.fun_def = fun_def

    def is_fatal(self):
        return False

    def fail_string(self):
        return "NoFunctionDocWarning[{}]@{}:{}".format(str(self.fun_def.ast.name)
                                                       , self.fun_def.ast.lineno
                                                       , self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr('Wrong definition'), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , tr("The function '{}' has no documentation.").format(self.fun_def.ast.name))



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
        return True

    def report(self, report):
        col_offset = self.node.ast.col_offset
        report.add_convention_error('error', tr('Declaration problem'), self.lineno, col_offset, self.explain)


class DeclarationWarning(TypeError):
    def __init__(self, in_function, node, category, lineno, explain):
        self.in_function = in_function
        self.node = node
        self.category = category
        self.lineno = lineno
        self.explain = explain

    def fail_string(self):
        return "DeclarationWarning[{}]@{}:{}".format(self.category
                                                     , self.lineno
                                                     , self.node.ast.col_offset)

    def is_fatal(self):
        return False

    def report(self, report):
        col_offset = self.node.ast.col_offset
        report.add_convention_error('warning', tr('Declaration problem'), self.lineno, col_offset, self.explain)

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
                                    , tr( "Expecting type '{}' but instead found: {}").format(self.expected_type, self.expr_type))

class TypeExpectationError(TypeError):
    def __init__(self, in_function, expr, expr_type, explain):
        self.in_function = in_function
        self.expr = expr
        self.expr_type = expr_type
        self.explain = explain

    def is_fatal(self):
        return True

    def fail_string(self):
        return "TypeExpectationError[{}/{}]@{}:{}".format(self.expr_type, self.explain, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Incorrect type"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("Found type '{}' which is incorrect: {}").format(self.expr_type, self.explain))


class TypeImprecisionWarning(TypeError):
    def __init__(self, in_function, expected_type, expr, expr_type, explain):
        self.in_function = in_function
        self.expected_type = expected_type
        self.expr = expr
        self.expr_type = expr_type

    def is_fatal(self):
        return False

    def fail_string(self):
        return "TypeImprecisionWarning[{}/{}]@{}:{}".format(self.expected_type, self.expr_type, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Imprecise typing"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("Expecting type '{}' but found '{}': there is a risk of imprecision (but it's maybe not a bug)").format(self.expected_type, self.expr_type))


class OptionCoercionWarning(TypeError):
    def __init__(self, expr, expr_option_type, expected_precise_type):
        self.expr = expr
        self.expected_precise_type = expected_precise_type
        self.expr_option_type = expr_option_type

    def is_fatal(self):
        return False

    def fail_string(self):
        return "OptionCoercionWarning[{}/{}]@{}:{}".format(self.expected_precise_type, self.expr_option_type, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Imprecise typing"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("Expecting type '{}' but found less precise type '{}' (the value could be None)").format(self.expected_precise_type, self.expr_option_type))


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
    def __init__(self, in_function, expected_type, ret_type, ret_expr):
        self.in_function = in_function
        self.expected_type = expected_type
        self.ret_type = ret_type
        self.ret_expr = ret_expr

    def is_fatal(self):
        return True

    def fail_string(self):
        return "WrongReturnTypeError[{}/{}]@{}:{}".format(self.expected_type, self.ret_type, self.ret_expr.ast.lineno, self.ret_expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Wrong return type"), self.ret_expr.ast.lineno, self.ret_expr.ast.col_offset
                                    , tr("The declared return type for function '{}' is '{}' but the return expression has incompatible type: {}").format(self.in_function.name, self.expected_type, self.ret_type))

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
    def __init__(self, method_call, param_types, arguments, call):
        self.method_call = method_call
        self.arguments = arguments
        self.param_types = param_types
        self.call = call

    def is_fatal(self):
        return True

    def fail_string(self):
        return "CallArityError[{}:{}/{}]@{}:{}".format(self.call.fun_name, len(self.param_types), len(self.arguments), self.call.ast.lineno, self.call.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Call problem"), self.call.ast.lineno, self.call.ast.col_offset
                                    , tr("calling '{}' with {} argument(s) but expecting: {}").format(self.call.fun_name
                                                                                                      , len(self.arguments)
                                                                                                      , len(self.param_types)))

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
    def __init__(self, compare, cond, left_type, right_type):
        self.compare = compare
        self.cond = cond
        self.left_type = left_type
        self.right_type = right_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "CompareConditionError[{}/{}]@{}:{}".format(self.left_type, self.right_type, self.compare.ast.lineno, self.compare.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Comparison error"), self.compare.ast.lineno, self.compare.ast.col_offset
                                    , tr("The two operands of the comparision should have the same type: '{}' vs. '{}'").format(self.left_type, self.right_type))

class CompareConditionWarning(TypeError):
    def __init__(self, compare, cond, left_type, right_type):
        self.compare = compare
        self.cond = cond
        self.left_type = left_type
        self.right_type = right_type

    def is_fatal(self):
        return False

    def fail_string(self):
        return "CompareConditionWarning[{}/{}]@{}:{}".format(self.left_type, self.right_type, self.compare.ast.lineno, self.compare.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Comparison issue"), self.compare.ast.lineno, self.compare.ast.col_offset
                                    , tr("The two operands of the comparison are only \"weakly\" compatibles: '{}' vs. '{}'").format(self.left_type, self.right_type))

class DeadVariableUseError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "DeadVariableUseError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of variable '{}' that is not in scope (Python101 scoping rule)").format(self.var_name))

class DeadVariableDefineError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "DeadVariableDefineError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of a \"dead\" variable name '{}' (Python101 rule)").format(self.var_name))

class GlobalVariableUseError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "GlobalVariableUseError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of global variable '{}' (Python101 rule)").format(self.var_name))

class VariableTypeError(TypeError):
    def __init__(self, target, var, declared_type, var_type):
        self.target = target
        self.var = var
        self.declared_type = declared_type
        self.var_type = var_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "VariableTypeError[{}:{}/{}]@{}:{}".format(self.var.var_name, self.var_type, self.declared_type, self.var.ast.lineno, self.var.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable type"), self.var.ast.lineno, self.var.ast.col_offset
                                    , tr("Type mismatch for variable '{}', expecting '{}' instead of: {}").format(self.var.var_name, self.declared_type, self.var_type))


class ParameterInAssignmentError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ParameterInAssignmentError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of parameter '{}' in assignment").format(self.var_name))

class ParameterInForError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ParameterInForError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of parameter '{}' as iteration variable").format(self.var_name))

class ParameterInCompError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ParameterInCompError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of parameter '{}' as comprehension variable").format(self.var_name))

class ParameterInWithError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ParameterInWithError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("Forbidden use of parameter '{}' in with construct").format(self.var_name))


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

class NaryNumOpArgNotNumeric(TypeError):
    def __init__(self, arg):
        self.arg = arg

    def is_fatal(self):
        return True

    def fail_string(self):
        return "NaryNumOpArgNotNumeric[]@{}:{}".format(self.arg.ast.lineno, self.arg.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad argument"), self.arg.ast.lineno, self.arg.ast.col_offset
                                    , tr("This argument is not numeric."))


class IndexingDictKeyTypeError(TypeError):
    def __init__(self, index, dict_key_type):
        self.index = index
        self.dict_key_type = dict_key_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "IndexingDictKeyTypeError[{}]@{}:{}".format(self.dict_key_type, self.index.ast.lineno, self.index.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad index"), self.index.ast.lineno, self.index.ast.col_offset
                                    , tr("Dictionnary key must be of type: {}").format(self.dict_key_type))


class SlicingError(TypeError):
    def __init__(self, slicing, subject_type):
        self.slicing = slicing
        self.subject_type = subject_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "SlicingError[{}]@{}:{}".format(self.subject_type, self.slicing.ast.lineno, self.slicing.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad slicing"), self.slicing.ast.lineno, self.slicing.ast.col_offset
                                    , tr("One can only slice a sequence (str, list), not a '{}'").format(self.subject_type))

class MembershipTypeError(TypeError):
    def __init__(self, container_expr, container_type):
        self.container_expr = container_expr
        self.container_type = container_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "MembershipTypeError[{}]@{}:{}".format(self.container_type, self.container_expr.ast.lineno, self.container_expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad membership"), self.container_expr.ast.lineno, self.container_expr.ast.col_offset
                                    , tr("Membership only supported for sets and dicts, not for type: {}").format(self.container_type))

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

class TupleTypeExpectationError(TypeError):
    def __init__(self, in_function, expr, expr_type):
        self.in_function = in_function
        self.expr = expr
        self.expr_type = expr_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "TupleTypeExpectationError[{}]@{}:{}".format(self.expr_type, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Incorrect type"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("Expecting an expression of tuple type, instead found type: '{}'").format(self.expr_type))



class UnknownTypeAliasError(TypeError):
    def __init__(self, typ, unknown_alias, lineno, col_offset):
        self.type = typ
        self.unknown_alias = unknown_alias
        self.lineno = lineno
        self.col_offset = col_offset

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnknownTypeAliasError[{}]@{}:{}".format(self.unknown_alias, self.lineno, self.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Type name error"), self.lineno, self.col_offset
                                    , tr("I don't find any definition for the type: {}").format(self.unknown_alias))


class ReservedFunctionNameError(TypeError):
    def __init__(self, fun_def, lineno, col_offset):
        self.fun_def = fun_def
        self.lineno = lineno
        self.col_offset = col_offset

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ReservedFunctionNameError[{}]@{}:{}".format(self.fun_def.name, self.lineno, self.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Wrong function name"), self.lineno, self.col_offset
                                    , tr("The function name '{}' is reserved in student mode").format(self.fun_def.name))

class MissingReturnTypeError(TypeError):
    def __init__(self, fun_def, lineno, col_offset):
        self.fun_def = fun_def
        self.lineno = lineno
        self.col_offset = col_offset

    def is_fatal(self):
        return True

    def fail_string(self):
        return "MissingReturnTypeError[{}]@{}:{}".format(self.fun_def.name, self.lineno, self.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Missing return type"), self.lineno, self.col_offset
                                    , tr("I don't find the return type for function: {}").format(self.fun_def.name))

class ExprAsInstrWarning(TypeError):
    def __init__(self, enode):
        self.enode = enode

    def is_fatal(self):
        return False

    def fail_string(self):
        return "ExprAsInstrWarning@{}:{}".format(self.enode.ast.lineno, self.enode.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Expression problem"), self.enode.ast.lineno, self.enode.ast.col_offset
                                    , tr("This expression is in instruction position, the computed value is lost"))

class NoReturnInFunctionError(TypeError):
    def __init__(self, fun_def):
        self.fun_def = fun_def

    def is_fatal(self):
        return True

    def fail_string(self):
        return "NoReturnInFunctionError[{}]@{}:{}".format(self.fun_def.name, self.fun_def.ast.lineno, self.fun_def.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Return problem"), self.fun_def.ast.lineno, self.fun_def.ast.col_offset
                                    , tr("The function '{}' should have `return` statement(s)").format(self.fun_def.name))


class ForbiddenMultiAssign(TypeError):
    def __init__(self, var):
        self.var = var

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ForbiddenMultiAssign[{}]@{}:{}".format(self.var.var_name, self.var.ast.lineno, self.var.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Assignment problem"), self.var.ast.lineno, self.var.ast.col_offset
                                    , tr("This assignment to variable '{}' is forbidden in Python101.").format(self.var.var_name))



class ERangeArgumentError(TypeError):
    def __init__(self, erange):
        self.erange = erange

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ERangeArgumentError@{}:{}".format(self.erange.ast.lineno, self.erange.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Range problem"), self.erange.ast.lineno, self.erange.ast.col_offset
                                    , tr("the arguments of `range` are incorrect."))

def typecheck_from_ast(ast, filename=None, source=None):
    prog = Program()
    if source is None:
        source = ""
    prog.build_from_ast(ast, filename, source)
    ctx = prog.type_check()
    return ctx

def typecheck_from_file(filename):
    prog = Program()
    prog.build_from_file(filename)
    ctx = prog.type_check()
    return ctx

class IteratorTypeError(TypeError):
    def __init__(self, for_node, iter_type):
        self.for_node = for_node
        self.iter_type = iter_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "IteratorTypeError[{}]@{}:{}".format(self.iter_type, self.for_node.iter.ast.lineno, self.for_node.iter.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad iterator"), self.for_node.iter.ast.lineno, self.for_node.iter.ast.col_offset
                                    , tr("Not an iterable type: {}").format(self.iter_type))



class IterVariableInEnvError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "IterVariableInEnvError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("The iterator variable '{}' is already in use.").format(self.var_name))

class WithVariableInEnvError(TypeError):
    def __init__(self, var_name, node):
        self.var_name = var_name
        self.node = node

    def is_fatal(self):
        return True

    def fail_string(self):
        return "WithVariableInEnvError[{}]@{}:{}".format(self.var_name, self.node.ast.lineno, self.node.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad variable"), self.node.ast.lineno, self.node.ast.col_offset
                                    , tr("The `with` variable '{}' is already declared").format(self.var_name))



class UnhashableElementError(TypeError):
    def __init__(self, st, element, element_type):
        self.set = st
        self.element = element
        self.element_type = element_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnhashableElementError[{}]@{}:{}".format(self.element_type, self.element.ast.lineno, self.element.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad set"), self.element.ast.lineno, self.element.ast.col_offset
                                    , tr("Unhashable (mutable) element forbidden in set, element type is: {}").format(self.element_type))


class UnhashableKeyError(TypeError):
    def __init__(self, edict, key, key_type):
        self.dict = edict
        self.key = key
        self.key_type = key_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "UnhashableKeyError@{}:{}".format(self.key.ast.lineno, self.key.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad dictionary"), self.key.ast.lineno, self.key.ast.col_offset
                                    , tr("Unhashable (mutable) key in dictionary, key type is: {}").format(self.key_type))


class ContainerAssignTypeError(TypeError):
    def __init__(self, cassign, container_type):
        self.cassign = cassign
        self.container_type = container_type

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ContainerAssignTypeError[{}]@{}:{}".format(self.container_type, self.cassign.container_expr.ast.lineno, self.cassign.container_expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad assignment"), self.cassign.container_expr.ast.lineno, self.cassign.container_expr.ast.col_offset
                                    , tr("In Python101 this kind of assignment is only available for dictionaries, not for objects of type: {}").format(self.container_type))

class ContainerAssignEmptyError(TypeError):
    def __init__(self, cassign):
        self.cassign = cassign

    def is_fatal(self):
        return True

    def fail_string(self):
        return "ContainerAssignEmptyError@{}:{}".format(self.cassign.container_expr.ast.lineno, self.cassign.container_expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Bad assignment"), self.cassign.container_expr.ast.lineno, self.cassign.container_expr.ast.col_offset
                                    , tr("Assignment in an empty dictionary"))


class EmptyTupleError(TypeError):
    def __init__(self, etup):
        self.etup = etup

    def is_fatal(self):
        return True

    def fail_string(self):
        return "EmptyTupleError@{}:{}".format(self.etup.ast.lineno, self.etup.ast.col_offset)

    def report(self, report):
        report.add_convention_error('error', tr("Empty tuple"), self.etup.ast.lineno, self.etup.ast.col_offset
                                    , tr("Python 101 does not allow empty tuples, only in expert mode"))


class SideEffectWarning(TypeError):
    def __init__(self, in_function, expr, fun_name, receiver, protected_var):
        self.in_function = in_function
        self.receiver = receiver
        self.fun_name = fun_name
        self.expr = expr
        self.protected_var = protected_var

    def is_fatal(self):
        return False

    def fail_string(self):
        return "SideEffectWarning[{}]@{}:{}".format(self.fun_name, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Call to '{}' may cause side effect").format(self.fun_name), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("There is a risk of side effect as on the following parameter(s) {}").format(self.protected_var))

class SideEffectContainerWarning(TypeError):
    def __init__(self, in_function, expr, fun_name, receiver, protected_var):
        self.in_function = in_function
        self.receiver = receiver
        self.fun_name = fun_name
        self.expr = expr
        self.protected_var = protected_var

    def is_fatal(self):
        return False

    def fail_string(self):
        return "SideEffectContainerWarning[{}]@{}:{}".format(self.fun_name, self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Assignment may cause side effect").format(self.fun_name), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("There is a risk of side effect as on the following parameter(s) {}").format(self.protected_var))

class CallNotNoneWarning(TypeError):
    def __init__(self, expr, call_type):
        self.expr = expr
        self.call_type = call_type

    def is_fatal(self):
        return False

    def fail_string(self):
        return "CallNotNoneWarning@{}:{}".format(self.expr.ast.lineno, self.expr.ast.col_offset)

    def report(self, report):
        report.add_convention_error('warning', tr("Expression in instruction position"), self.expr.ast.lineno, self.expr.ast.col_offset
                                    , tr("The value calculated of type `{}` is lost").format(self.call_type))

if __name__ == '__main__':

    import sys
    prog1 = Program()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "../../mrpython/aa_pstl/aire_mixte.py"

    ctx = typecheck_from_file(filename)
    print(repr(ctx))
