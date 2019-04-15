import os.path, sys
import ast
import math


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
    from type_parser import (type_expression_parser, function_type_parser, var_type_parser, type_def_parser)

    from translate import tr
else:
    from .prog_ast import *
    from .type_ast import *
    from .type_parser import (type_expression_parser, function_type_parser, var_type_parser, type_def_parser)

    from .translate import tr

"""
def dag_from_ast(ast, filename=None, source=None):
    prog = Program()
    prog.build_from_ast(ast, filename, source)
    ctx = prog.type_check()
    return ctx
"""

class BB():
    def __init__(self, instrs, last_instr):
        self.instrs = instrs
        self.last_instr = last_instr
    
    def is_return(self):
        return isinstance(last_instr, Return)
    
    def __str__(self):
        s = ""
        for instr in self.instrs:
            s += str(instr) + ","
        return s


class Nod():
    def __init__(self, ret):
        self.ret = ret
        self.voisins = []
    
    def add_voisin(self, v):
        self.voisins.append(v)

class DAG():
    def __init__(self):
        self.l_nod = []
    
    def add_nod(self, ret):
        self.l_nod.append(Nod(ret))
        
    def add_vertices(self, n1, n2):
        l_nod[n1].add_voisin(n2)
        
def is_branch(instr):
    print("hi")
    return isinstance(instr, If) or isinstance(instr, While) or isinstance(instr, For) or isinstance(instr, Return)

def visit_prog(prog):
    for (fname, f) in prog.functions.items():
        print(fname)
        f.visitDAG()
            
Program.visitDAG = visit_prog



def visit_function(f):
    g = DAG()
    pred = []
    l_instr = []
    l_BB = []
    for instr in f.body:
        l_instr.append(instr)
        if is_branch(instr):
            l_BB.append(BB(l_instr, instr))
            l_instr = []
    for bb in l_BB:
        print(bb)
       
FunctionDef.visitDAG = visit_function

def visit_for(instr, G):
    print("for")
For.visitDAG = visit_for

def visit_return(instr, G):
    print("return")
Return.visitDAG = visit_return

def computeBB_if(ifinstr, l_BB):
    pass
    #for instr in ifinstr.body:
        
    
If.computeBB = computeBB_if

def visit_while(instr, G):
    print("while")
While.visitDAG = visit_while

"""
def visit_import(instr, G):
    pass
Import.visitDAG = visit_import

def visit_testCase(instr):
    pass
TestCase.visitDAG = visit_testCase

def visit_LHSVar(instr, G):
    pass
LHSVar.visitDAG = visit_LHSVar

def visit_LHSTuple(instr, G):
    pass
LHSTuple.visitDAG = visit_LHSTuple


def visit_assign(instr, G):
    pass
Assign.visitDAG = visit_assign

def visit_containerAssign(instr, G):
    pass
ContainerAssign.visitDAG = visit_containerAssign



def visit_assertion(instr, G):
    pass
Assertion.visitDAG = visit_assertion

def visit_with(instr, G):
    pass
With.visitDAG = visit_with


def visit_expr(e, G):
    pass
Expr.visitDAG = visit_expr
"""
def dag_from_file(filename):
    prog = Program()
    prog.build_from_file(filename)
    prog.visitDAG()
    #ctx = prog.type_check()
    return None


dag_from_file("tuple_effect.py")
"""The abstract syntax tree of programs."""
"""

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
"""

"""

        

class For:
        
class Return:



class If:

class While:


"""