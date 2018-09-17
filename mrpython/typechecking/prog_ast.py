
"""The abstract syntax tree of programs."""

import ast
import tokenize

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

        # other top level definitions
        self.other_top_defs = []

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
        if filename:
            self.filename = filename
        if source:
            self.source = source

        if not isinstance(modast, ast.Module):
            raise ValueError("Cannot build program from AST: not a module (please report)")
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
            elif isinstance(node, ast.Assign):
                assign_ast = Assign(node)
                self.global_vars.append(assign_ast)
            else:
                #print("Unsupported instruction: " + node)
                self.other_top_defs.append(UnsupportedNode(node))

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
        #print(astpp.dump(self.ast))
        self.python101ready = True

        self.parameters = []
        for arg_obj in self.ast.args.args:
            self.parameters.append(arg_obj.arg)

        first_instr = self.ast.body[0]
        next_instr_index = 0
        if isinstance(first_instr, ast.Expr) and isinstance(first_instr.value, ast.Str):
            self.docstring = first_instr.value.s
            next_instr_index = 1
            #print(self.docstring)
        else:
            self.python101ready = False

        self.body = []
        for inner_node in self.ast.body[next_instr_index:]:
            #print(astpp.dump(inner_node))
            self.body.append(parse_instruction(inner_node))


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
        raise NotSupportedError("Can only destructure names and tuples (please report)")    
        
class Assign:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))

        self.target = build_lhs_destruct(self.ast.targets[0])

        self.expr = parse_expression(self.ast.value)

class For:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))

        self.target = build_lhs_destruct(self.ast.target)

        self.iter = parse_expression(node.iter)
        self.body = []
        for instr in node.body:
            iinstr = parse_instruction(instr)
            self.body.append(iinstr)

        
class Return:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.expr = parse_expression(self.ast.value)

class If:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
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
        #print(astpp.dump(node))
        self.cond = parse_expression(self.ast.test)
        self.body = []
        for instr in self.ast.body:
            iinstr = parse_instruction(instr)
            self.body.append(iinstr)

def parse_expression_as_instruction(node):
    # XXX: do something here or way until typing for
    #      losing the returned value (except if None)
    # For now, just parse as an expression
    return parse_expression(node.value)

INSTRUCTION_CLASSES = {"Assign" : Assign
                       , "Return" : Return
                       , "If" : If
                       , "While" : While
                       , "Expr" : parse_expression_as_instruction
                       , "For" : For
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

class ENum:
    def __init__(self, node):
        self.ast = node
        self.value = node.n

class EStr:
    def __init__(self, node):
        self.ast = node
        self.value = node.s

class ETrue:
    def __init__(self, node):
        self.ast = node

class EFalse:
    def __init__(self, node):
        self.ast = node

class ENone:
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

class EVar:
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

class ETuple:
    def __init__(self, node):
        self.ast = node
        self.elements = []
        for elem_node in node.elts:
            elem = parse_expression(elem_node)
            self.elements.append(elem)
        
class EAdd:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class ESub:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EMult:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EDiv:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EFloorDiv:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right
        
class EMod:
    def __init__(self, node, left, right):
        self.ast = node
        self.left = left
        self.right = right

class EPow:
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
        return UnsupportedNode(node)

class EAnd:
    def __init__(self, node, operands):
        self.ast = node
        self.operands = operands

class EOr:
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

class EUSub:
    def __init__(self, node, operand):
        self.ast = node
        self.operand = operand

class ENot:
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


class ECompare:
    def __init__(self, node, conds):
        self.ast = node
        self.conds = conds

def parse_compare(node):
    #print(astpp.dump(node))
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


COMPARE_CLASSES = { "Eq" : CEq
                    , "NotEq" : CNotEq
                    , "GtE" : CGtE
                    , "Gt" : CGt
                    , "LtE" : CLtE
                    , "Lt" : CLt
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

class ECall:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))

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

class EList:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.elements = []
        for elt in node.elts:
            elt_expr = parse_expression(elt)
            self.elements.append(elt_expr)

class Indexing:
    def __init__(self, node):
        self.ast = node
        self.subject = parse_expression(node.value)
        self.index = parse_expression(node.slice.value)

class Slicing:
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
            self.step = parse_expression(node.slice.upper)

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
        
class EListComp:
    def __init__(self, node):
        self.ast = node
        #print(astpp.dump(node))
        self.compr_expr = parse_expression(node.elt)
        self.generators = []
        for gen in node.generators:
            self.generators.append(Generator(gen))
            
EXPRESSION_CLASSES = { "Num" : ENum
                       , "Str" : EStr
                       , "NameConstant"  : parse_constant
                       , "Name" : EVar
                       , "Attribute" : EVar
                       , "Tuple" : ETuple
                       , "BinOp" : EBinOp
                       , "BoolOp" : EBoolOp
                       , "UnaryOp" : EUnaryOp
                       , "Call" : ECall
                       , "Compare" : parse_compare
                       , "List" : EList
                       , "Subscript" : parse_subscript
                       , "ListComp" : EListComp
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
    prog1 = Program()
    prog1.build_from_file("../../examples/aire.py")
    #print(astpp.dump(prog1.ast))
