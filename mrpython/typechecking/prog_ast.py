"""The abstract syntax tree of programs."""

import ast
import tokenize

try:
    from .type_ast import *
except ImportError:
    from type_ast import *

try:
    from .type_converter import *
except ImportError:
    from type_converter import *

import os.path, sys

main_path = os.path.dirname(os.path.realpath(__file__))
found_path = False
for path in sys.path:
    if path == main_path:
        found_path = True
        break
if not found_path:
    sys.path.append(main_path)


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

        # global (read-only) variables
        self.global_vars = []

        # type aliases (extracted from the global_vars)
        self.type_aliases = []

        # other top level definitions
        self.other_top_defs = []

        #multi-declared functions
        self.multi_declared_functions = dict()

        # metadata
        self.filename = None
        self.source = None
        self.source_lines = None
        self.ast = None

    def get_source_line(self, linum):
        if self.source is None:
            raise ValueError("Source is empty")
        if self.source_lines is None:
            self.source_lines = self.source.split('\n')

        return self.source_lines[linum-1]

    def build_from_file(self, filename):
        self.filename = filename
        modtxt = ""
        with tokenize.open(filename) as f:
            modtxt = f.read()
        self.source = modtxt
        modast = ast.parse(modtxt, mode="exec")
        self.build_from_ast(modast)

    def build_from_ast(self, modast, filename=None, source=None):
        if filename is not None:
            self.filename = filename

        if source is not None:
            self.source = source

        if not isinstance(modast, ast.Module):
            raise ValueError("Cannot build program from AST: not a module (please report)")
        self.ast = modast

        for node in modast.body:
            #print(str(dir(node)))
            if isinstance(node, ast.Import):
                imp_ast = Import(node)
                self.imports[imp_ast.name] = imp_ast
            elif isinstance(node, ast.ImportFrom):
                if not check_typing_imports(node):
                    self.other_top_defs.append(UnsupportedNode(node))
            elif isinstance(node, ast.FunctionDef):
                fun_ast = FunctionDef(node)
                if fun_ast.python101ready:
                    if fun_ast.name in self.functions:
                        self.multi_declared_functions[fun_ast.name] = node.lineno
                    else:
                        self.functions[fun_ast.name] = fun_ast
                else:
                    self.other_top_defs.append(UnsupportedNode(node))
            elif isinstance(node, ast.Assert):
                assert_ast = TestCase(node)
                self.test_cases.append(assert_ast)
            elif isinstance(node, ast.AnnAssign) and node.value is None:
                DeclareVar_ast = DeclareVar(node)
                self.global_vars.append(DeclareVar_ast)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                if not check_typevar_assign(node):
                    if isinstance(node, ast.AnnAssign):
                        # Type annotation with initialization
                        DeclareVar_ast = DeclareVar(node)
                        self.global_vars.append(DeclareVar_ast)
                    # assignment is also a global variables
                    assign_ast = Assign(node)
                    self.global_vars.append(assign_ast)
                # else do nothing for typevar declarations
            else:
                # print("Unsupported instruction: " + node)
                self.other_top_defs.append(UnsupportedNode(node))

ALLOWED_TYPING_IMPORTS = { 'Optional', 'Tuple', 'List', 'Dict', 'Set', 'TypeVar' }

def check_typing_imports(node):
    if node.module != "typing":
        return False
    for alias in node.names:
        if alias.name not in ALLOWED_TYPING_IMPORTS:
            return False
    return True

def check_typevar_assign(node):
    # TODO : more precise error checking
    if isinstance(node, ast.AnnAssign):
        return False # TODO : handle this case more precisely, why not  T : TypeVar = TypeVar('T') ?
    if len(node.targets) != 1:
        return False
    if node.targets[0].id not in PREDEFINED_TYPE_VARIABLES:
        return False
    if node.value.func.id != 'TypeVar':
        return False
    if len(node.value.args) != 1:
        return False
    if node.value.args[0].s != node.targets[0].id:
        return False

    return True


class UnsupportedNode:
    def __init__(self, node):
        self.ast = node
        #print("Unsupported node:", astpp.dump(node))

class Import:
    def __init__(self, node):
        self.ast = node
        #print_ast_fields(self.ast)
        alias = self.ast.names[0]
        self.name = alias.name
class FunctionDef:
    def __init__(self, node):
        self.ast = node
        self.name = self.ast.name
        self.python101ready = True

        self.param_types = []
        self.parameters = []

        self.preconditions = []
        for arg_obj in self.ast.args.args:
            self.parameters.append(arg_obj.arg)

        for arg_obj in self.ast.args.args:
            self.param_types.append(arg_obj.annotation)

        first_instr = self.ast.body[0]
        next_instr_index = 0
        self.docstring = None
        if isinstance(first_instr, ast.Expr) and isinstance(first_instr.value, ast.Str):
            self.docstring = first_instr.value.s
            next_instr_index = 1
            splitedDocstring = self.docstring.splitlines()
            i = 0
            for s in splitedDocstring:
                if("précondition" in s.lower() or "precondition" in s.lower()):
                    j = 0
                    precondition = s.split(":")[1].strip()
                    if precondition == "":
                        precondition = splitedDocstring[i+1].strip()
                        j = 1
                    if precondition != "":
                        try:
                            precondition_ast = ast.parse(precondition, mode="eval")
                            precondition_ast.lineno = first_instr.lineno + i + j
                            if(hasattr(precondition_ast,"body")):
                                precondition_node = parse_expression(precondition_ast.body)
                                self.preconditions.append((precondition_node, precondition_ast))
                            else:
                                raise ValueError("Precondition not supported (please report): {}".format(precondition_ast))
                        except SyntaxError:
                            pass
                elif ("hypothese" in s.lower() or "hypothèse" in s.lower()):
                    j = 0
                    precondition = s.split(":")[1].strip()
                    if precondition == "":
                        precondition = splitedDocstring[i+1].strip()
                        j = 1
                    if precondition != "":
                        try:
                            precondition_ast = ast.parse(precondition, mode="eval")
                            precondition_ast.lineno = first_instr.lineno + i + j
                            if(hasattr(precondition_ast,"body")):
                                precondition_node = parse_expression(precondition_ast.body)
                                self.preconditions.append((precondition_node, precondition_ast))
                            else:
                                raise ValueError("Precondition not supported (please report): {}".format(precondition_ast))
                        except SyntaxError:
                            pass
                i = i + 1
            #print(self.docstring)
        else:
            # nothing to do ?
            pass

        self.body = []
        for inner_node in self.ast.body[next_instr_index:]:
            self.body.append(parse_instruction(inner_node))

        self.returns = self.ast.returns

class TestCase:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))

        self.expr = parse_expression(self.ast.test)

class LHSVar:
    def __init__(self, node):
        self.ast = node
        self.var_name = node.id

    def variables(self):
        return [self]

    def arity(self):
        return 1

    def __str__(self):
        return self.var_name

    def __repr__(self):
        return "LHSVar({})".format(self.var_name)

class LHSTuple:
    def __init__(self, node, elements):
        self.ast = node
        self.elements = elements
        #print(dir(node))

    def variables(self):
        vs = []
        for element in self.elements:
            vs.extend(element.variables())
        return vs

    def arity(self):
        return len(self.elements)

    def __str__(self):
        return ", ".join( ( str(elt) for elt in self.elements) )

    def __repr__(self):
        return "LHSTuple({})".format(", ".join ( ( repr(elt) for elt in self.elements ) ))

def build_lhs_destruct(node):
    if isinstance(node, ast.Name):
        return LHSVar(node)
    elif isinstance(node, ast.Tuple):
        elements = []
        for elt in node.elts:
            elements.append(build_lhs_destruct(elt))
        return LHSTuple(node, elements)
    else:
        return UnsupportedNode(node)

class Assign:
    def __init__(self, node):

        self.ast = node

        if isinstance(node, ast.AnnAssign):
            self.type_annotation = self.ast.annotation
            self.target = build_lhs_destruct(self.ast.target)

        else:
            self.target = build_lhs_destruct(self.ast.targets[0])

        self.expr = parse_expression(self.ast.value)

class DeclareVar:
    def __init__(self, node):
        self.ast = node
        self.type_annotation = self.ast.annotation
        self.target = build_lhs_destruct(self.ast.target)

class ContainerAssign:
    def __init__(self, target, expr):
        self.container_expr = parse_expression(target.value)
        self.container_index = parse_expression(target.slice.value)
        self.assign_expr = parse_expression(expr)


def parse_assign(node):

    if isinstance(node, ast.AnnAssign) and node.value is None:
        return DeclareVar(node)
    else:

        if isinstance(node, ast.AnnAssign):
            if node.target and isinstance(node.target, ast.Subscript):
                return ContainerAssign(node.target, node.value)
        else:
            # dictionary (container) assignment
            if node.targets and isinstance(node.targets[0], ast.Subscript):
                return ContainerAssign(node.targets[0], node.value)

    # other form of assigment
    assign = Assign(node)
    if isinstance(assign.target, UnsupportedNode):
        return assign.target
    else:
        return assign

class For:
    def __init__(self, node):
        self.ast = node

        self.target = build_lhs_destruct(self.ast.target)

        self.iter = parse_expression(node.iter)
        self.body = []
        for instr in node.body:
            iinstr = parse_instruction(instr)
            self.body.append(iinstr)


class Return:
    def __init__(self, node):
        self.ast = node
        self.expr = parse_expression(self.ast.value)

def parse_return(node):
    if node.value:
        return Return(node)
    else:
        return UnsupportedNode(node)

class If:
    def __init__(self, node):
        self.ast = node
        self.cond = parse_expression(self.ast.test)
        self.body = []
        for instr in self.ast.body:
            iinstr = parse_instruction(instr)
            self.body.append(iinstr)
        self.orelse = []
        for instr in self.ast.orelse:
            iinstr = parse_instruction(instr)
            self.orelse.append(iinstr)

class While:
    def __init__(self, node):
        self.ast = node
        self.cond = parse_expression(self.ast.test)
        self.body = []
        for instr in self.ast.body:
            iinstr = parse_instruction(instr)
            self.body.append(iinstr)

class Assertion:
    def __init__(self, node):
        self.ast = node
        self.test = parse_expression(self.ast.test)

class With:
    def __init__(self, node, call, var_name, body):
        self.ast = node
        self.call = call
        self.var_name = var_name
        self.body = body

def parse_with(node):
    if not node.items:
        return UnsupportedNode(node)

    with_call = node.items[0].context_expr
    if not isinstance(with_call, ast.Call):
        return UnsupportedNode(node)
    with_call = parse_expression(with_call)

    if not node.items[0].optional_vars:
        return UnsupportedNode(node)

    with_var = node.items[0].optional_vars.id

    with_body = []
    for instr in node.body:
        iinstr = parse_instruction(instr)
        with_body.append(iinstr)

    return With(node, with_call, with_var, with_body)

def parse_expression_as_instruction(node):
    # XXX: do something here or way until typing for
    #      losing the returned value (except if None)
    # For now, just parse as an expression
    return parse_expression(node.value)

INSTRUCTION_CLASSES = {"Assign" : parse_assign
                       , "AnnAssign" : parse_assign
                       , "Return" : parse_return
                       , "If" : If
                       , "While" : While
                       , "Expr" : parse_expression_as_instruction
                       , "For" : For
                       , "Assert" : Assertion
                       , "With" : parse_with
}

def parse_instruction(node):
    instruction_type_name = node.__class__.__name__
    #print("instruction type=",instruction_type_name)
    if instruction_type_name in INSTRUCTION_CLASSES:
        wrap_node = INSTRUCTION_CLASSES[instruction_type_name](node)
        return wrap_node
    else:
        #print(">>>> not supported")
        return UnsupportedNode(node)

class Expr:
    pass

class ENum(Expr):
    def __init__(self, node, setval=None):
        self.ast = node
        if setval is not None:
            self.value = setval
        else:
            self.value = node.n

class EStr(Expr):
    def __init__(self, node, setval=None):
        self.ast = node
        if setval is not None:
            self.value = setval
        else:
            self.value = node.s

class ETrue(Expr):
    def __init__(self, node):
        self.ast = node

class EFalse(Expr):
    def __init__(self, node):
        self.ast = node

class ENone(Expr):
    def __init__(self, node):
        self.ast = node

def parse_constant(node):
    if node.value is True:
        return ETrue(node)
    elif node.value is False:
        return EFalse(node)
    elif node.value is None:
        return ENone(node)

    raise ValueError("Constant not supported: {} (please report)".format(node.value))

# XXX: this is a hack for Python>=3.8 because
# they removed the type information in the constant parsing...
def parse_constant_expr(node):
    if node.value is True:
        return ETrue(node)
    elif node.value is False:
        return EFalse(node)
    elif node.value is None:
        return ENone(node)
    elif isinstance(node.value, (int, float, complex)):
        return ENum(node, setval=node.value)
    elif isinstance(node.value, str):
        return EStr(node, setval=node.value)

    raise ValueError("Constant not supported: {} (please report)".format(node.value))

class EVar(Expr):
    def __init__(self, node):
        self.ast = node
        if isinstance(self.ast, ast.Name):
            self.name = self.ast.id
        elif isinstance(self.ast, ast.Attribute):
            node = self.ast
            names = []
            while isinstance(node, ast.Attribute):
                names.append(node.attr)
                node = node.value

            if not isinstance(node, ast.Name):
                raise ValueError("Node is not a Name (please report)")

            names.append(node.id)
            names.reverse()
            self.name = ".".join(names)

        else:
            raise NotImplementedError("Unsupported EVar type (please report): {}".format(self.ast))

class ETuple(Expr):
    def __init__(self, node):
        # print("tuple : " + str(dir(node)) + "\n")
        # print("elts: " + str(dir(node.elts)))
        # print("_attributes: " + str(dir(node._attributes)))
        # print("_fields: " + str(dir(node._fields)))
        # print("node : " + str(type(node)))
        self.ast = node
        self.elements = []
        for elem_node in node.elts:
            elem = parse_expression(elem_node)
            self.elements.append(elem)

class EAdd(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class ESub(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EMult(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EDiv(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EFloorDiv(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EMod(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EPow(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EBitOr(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EBitAnd(Expr):
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

BINOP_CLASSES = { "Add" : EAdd
                  , "Sub" : ESub
                  , "Mult" : EMult
                  , "Div" : EDiv
                  , "FloorDiv" : EFloorDiv #  // vs. /
                  , "Mod" : EMod
                  , "Pow" : EPow
                  , "BitOr" : EBitOr
                  , "BitAnd" : EBitAnd
}

def EBinOp(node):
    #print(astpp.dump(node))
    binop_type_name = node.op.__class__.__name__
    #print("binop type=",binop_type_name)
    if binop_type_name in BINOP_CLASSES:
        left = parse_expression(node.left)
        right = parse_expression(node.right)
        wrap_node = BINOP_CLASSES[binop_type_name](node, left, right)
        return wrap_node
    else:
        print(astpp.dump(node))
        return UnsupportedNode(node)

class EAnd(Expr):
    def __init__(self, node, operands):
        self.ast = node
        self.operands = operands

class EOr(Expr):
    def __init__(self, node, operands):
        self.ast = node
        self.operands = operands

BOOLOP_CLASSES = { "And" : EAnd
                  , "Or" : EOr
}

def EBoolOp(node):
    boolop_type_name = node.op.__class__.__name__
    #print("boolop type=",boolop_type_name)
    if boolop_type_name in BOOLOP_CLASSES:
        operands = []
        for operand in node.values:
            operand = parse_expression(operand)
            operands.append(operand)

        wrap_node = BOOLOP_CLASSES[boolop_type_name](node, operands)
        return wrap_node
    else:
        return UnsupportedNode(node)

class EUSub(Expr):
    def __init__(self, node, operand):
        self.ast = node
        self.operand = operand

class ENot(Expr):
    def __init__(self, node, operand):
        self.ast = node
        self.operand = operand

UNOP_CLASSES = { "USub" : EUSub
                 , "Not" : ENot
}

def EUnaryOp(node):
    unop_type_name = node.op.__class__.__name__
    if unop_type_name in UNOP_CLASSES:
        operand = parse_expression(node.operand)
        return UNOP_CLASSES[unop_type_name](node, operand)
    else:
        return UnsupportedNode(node)


class ECompare(Expr):
    def __init__(self, node, conds):
        self.ast = node
        self.conds = conds

def parse_compare(node):
    #print(.dump(node))
    left = node.left
    conds = []
    for (op, right) in zip(node.ops, node.comparators):
        eleft = parse_expression(left)
        if isinstance(eleft, UnsupportedNode):
            return UnsupportedNode(node)
        eright = parse_expression(right)
        if isinstance(right, UnsupportedNode):
            return UnsupportedNode(node)
        econd = parse_cond(op, eleft, eright)
        if econd is None:
            return UnsupportedNode(node)
        conds.append(econd)
        left = right

    return ECompare(node, conds)

class Condition:
    def __init__(self, op, left, right):
        self.ast = op
        self.left = left
        self.right = right

class CEq(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CNotEq(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CGtE(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CGt(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CLtE(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CLt(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CIn(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

class CNotIn(Condition):
    def __init__(self, op, left, right):
        super().__init__(op, left, right)

COMPARE_CLASSES = { "Eq" : CEq
                    , "NotEq" : CNotEq
                    , "GtE" : CGtE
                    , "Gt" : CGt
                    , "LtE" : CLtE
                    , "Lt" : CLt
                    , "In" : CIn
                    , "NotIn" : CNotIn
}

def parse_cond(op, left, right):
    compare_type_name = op.__class__.__name__
    if compare_type_name in COMPARE_CLASSES:
        return COMPARE_CLASSES[compare_type_name](op, left, right)
    else:
        return None

def parse_function(func_descr):
    parts = []
    val = func_descr
    while isinstance(val, ast.Attribute):
        parts.append(parse_expression(val.value))
        val = val.value
    parts.append(val.id)
    #print("parts={}".format(parts))
    return parts

class ECall(Expr):
    def __init__(self, node):
        self.ast = node

        if isinstance(node.func, ast.Name):
            self.receiver = None
            self.fun_name = node.func.id
            self.full_fun_name = self.fun_name
            self.multi_receivers = False
        else: # attribute
            self.receiver = parse_expression(node.func.value)
            self.fun_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                self.multi_receivers = False
            else:
                self.multi_receivers = True
            self.full_fun_name = (node.func.value.id if not self.multi_receivers else "<multi-reicevers>") + "." + self.fun_name

        #print("function receiver={}".format(self.receiver))
        #print("function name=", self.fun_name)
        self.arguments = []

        for arg in self.ast.args:
            #print(astpp.dump(arg))
            earg = parse_expression(arg)
            self.arguments.append(earg)
            #print("---")

class ERange(Expr):
    def __init__(self, node):

        self.ast = node
        self.start = None
        if len(node.args) >= 1:
            self.start = parse_expression(node.args[0])
        self.stop = None
        if len(node.args) >= 2:
            self.stop = parse_expression(node.args[1])
        self.step = None
        if len(node.args) == 3:
            self.step = parse_expression(node.args[1])
        if len(node.args) > 3:
            self.start = None
            self.stop = None
            self.step = None

        if self.start is not None and self.stop is None:
            self.stop = self.start
            self.start = None

def parse_args(args):
    eargs = []
    for arg in args:
        eargs.append(parse_expression(arg))
    return eargs

def parse_call(node):
    if isinstance(node.func, ast.Name) and node.func.id == 'range':
        return ERange(node)
    elif isinstance(node.func, ast.Name) and node.func.id == 'min':
        return EMin(node, parse_args(node.args))
    elif isinstance(node.func, ast.Name) and node.func.id == 'max':
        return EMax(node, parse_args(node.args))
    elif isinstance(node.func, (ast.Name, ast.Attribute)):
        return ECall(node)
    else:
        return UnsupportedNode(node)


class EMin(Expr):
    def __init__(self, node, args):
        self.ast = node
        self.args = args

class EMax(Expr):
    def __init__(self, node, args):
        self.ast = node
        self.args = args

class EList(Expr):
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.elements = []
        for elt in node.elts:
            elt_expr = parse_expression(elt)
            self.elements.append(elt_expr)

class Indexing(Expr):
    def __init__(self, node):
        self.ast = node
        self.subject = parse_expression(node.value)
        self.index = parse_expression(node.slice.value)

class Slicing(Expr):
    def __init__(self, node):
        self.ast = node
        self.subject = parse_expression(node.value)
        self.lower = None
        if node.slice.lower is not None:
            self.lower = parse_expression(node.slice.lower)
        self.upper = None
        if node.slice.upper is not None:
            self.upper = parse_expression(node.slice.upper)
        self.step = None
        if node.slice.step is not None:
            self.step = parse_expression(node.slice.step)

def parse_subscript(node):
    if isinstance(node.slice, ast.Index):
        return Indexing(node)
    else:
        return Slicing(node)

class Generator:
    def __init__(self, generator):
        self.ast = generator
        self.target = build_lhs_destruct(self.ast.target)
        self.iter = parse_expression(self.ast.iter)
        self.conditions  = []
        for ifcond in self.ast.ifs:
            self.conditions.append(parse_expression(ifcond))

class EListComp(Expr):
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.compr_expr = parse_expression(node.elt)
        self.generators = []
        for gen in node.generators:
            self.generators.append(Generator(gen))

class ESet(Expr):
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.elements = []
        for elt in node.elts:
            elt_expr = parse_expression(elt)
            self.elements.append(elt_expr)

class ESetComp(Expr):
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.compr_expr = parse_expression(node.elt)
        self.generators = []
        for gen in node.generators:
            self.generators.append(Generator(gen))

class EDict(Expr):
    def __init__(self, node):
        self.ast = node
        self.keys = []
        for key in node.keys:
            key_expr = parse_expression(key)
            self.keys.append(key_expr)

        self.values = []
        for val in node.values:
            val_expr = parse_expression(val)
            self.values.append(val_expr)

class EDictComp(Expr):
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.key_expr = parse_expression(node.key)
        self.val_expr = parse_expression(node.value)
        self.generators = []
        for gen in node.generators:
            self.generators.append(Generator(gen))


EXPRESSION_CLASSES = { "Num" : ENum
                       , "Constant" : parse_constant_expr
                       , "Str" : EStr
                       , "NameConstant"  : parse_constant
                       , "Name" : EVar
                       , "Attribute" : EVar
                       , "Tuple" : ETuple
                       , "BinOp" : EBinOp
                       , "BoolOp" : EBoolOp
                       , "UnaryOp" : EUnaryOp
                       , "Call" : parse_call
                       , "Compare" : parse_compare
                       , "List" : EList
                       , "Set" : ESet
                       , "Dict" : EDict
                       , "Subscript" : parse_subscript
                       , "ListComp" : EListComp
                       , "SetComp" : ESetComp
                       , "DictComp" : EDictComp
}

def parse_expression(node):
    expression_type_name = node.__class__.__name__
    #print("expression type=",expression_type_name)
    if expression_type_name in EXPRESSION_CLASSES:
        wrap_node = EXPRESSION_CLASSES[expression_type_name](node)
        return wrap_node
    else:
        return UnsupportedNode(node)


def print_ast_fields(node):
    for field, val in ast.iter_fields(node):
        print(field)


def python_ast_from_file(filename):
    with tokenize.open(filename) as f:
        modtxt = f.read()
        modast = ast.parse(modtxt, mode="exec")
        return modast

def python_show_tokenized(filename):
    modtxt = ""
    with tokenize.open(filename) as f:
        modtxt = f.read()

    return modtxt

if __name__ == "__main__":
    import sys
    prog1 = Program()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "../../examples/revstr.py"

    prog1.build_from_file(filename)
    #print(astpp.dump(prog1.ast))
