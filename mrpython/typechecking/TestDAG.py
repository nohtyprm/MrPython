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
2 things can be done
-> check for return in all code branches (cannot access a nod with no successor which is not a return (implicit return))
-> check for dead code : identify strong connex components of the graph, rest is dead-code
"""

class Nod():
    def __init__(self, l_instr, ident, ret):
        self.ret = ret
        self.l_instr = l_instr
        self.ident = ident
        self.voisins = []
    
    def add_voisin(self, v):
        self.voisins.append(v)
    
    def is_return(self):
        return self.ret
        
    def __str__(self):
        s = "[Ret:"
        s += str(self.ret) + ", Voisins:{"
        for v in self.voisins:
            s += str(v) + " "
        s += "}, LInstr : " + str(self.l_instr)+"]"
        return s
    
class DAG():
    def __init__(self):
        self.l_nod = []
        self.nb_nods = 0
    
    def add_nod(self, l_instr, ret = False):
        self.l_nod.append(Nod(l_instr, self.nb_nods, ret))
        self.nb_nods = self.nb_nods + 1
        return self.nb_nods - 1
        
    def add_vertice(self, n1, n2):
        self.l_nod[n1].add_voisin(n2)
    
    def add_vertices(self, l_n1, n2):
        for n1 in l_n1:
            self.l_nod[n1].add_voisin(n2)
    
    def init(self):
        return self.l_nod[0]

    #only one terminating nod by definition of compute_block_function
    def is_term(self, n):
        return n is self.l_nod[self.nb_nods-1]
    
    def get_nod(self, n):
        return self.l_nod[n]
    
    def is_return_defined(self):
        marked = []
        for i in range(self.nb_nods):
            marked.append(False)
            
        fifo = []
        start = self.init()
        fifo.append(start)
        marked[start.ident] = True
        while fifo:
            nod = fifo.pop()
            if self.is_term(nod):
                print("return may be missing")
            for v in nod.voisins:
                if not marked[v]:
                    fifo.append(self.get_nod(v))
                    marked[v] = True
                    
    def dead_code(self):
        marked = []
        for i in range(self.nb_nods):
            marked.append(False)
        fifo = []
        start = self.init()
        fifo.append(start)
        marked[start.ident] = True
        while fifo:
            nod = fifo.pop()
            for v in nod.voisins:
                if not marked[v]:
                    fifo.append(self.get_nod(v))
                    marked[v] = True
        print(marked)
        for i in range(self.nb_nods):
            if not marked[i]:
                print("hi")
                instrs = self.get_nod(i).l_instr
                if instrs:
                    print("dead code")
                    print(instrs)
    
    def __str__(self):
        s = ""
        for n in self.l_nod:
            s += str(n) + "\n"
        return s
        
    
"""
G is in topologic order by construction, we can start from first nod then
"""

        
        
def is_branch(instr):
    return isinstance(instr, If) or isinstance(instr, While) or isinstance(instr, For) or isinstance(instr, Return)

def visit_prog(prog):
    for (fname, f) in prog.functions.items():
        print(fname)
        f.compute_block()
            
Program.visitDAG = visit_prog


def compute_block_block(b, G):
    l_instr = []
    head = None
    res = 0
    succ = []
    prv_succ = []
    #print (b)
    for instr in b:
        l_instr.append(instr)
        if is_branch(instr):
            (res,succ) = instr.compute_block(G, l_instr)
            l_instr = []
            
            if head is None:
                head = res
            else:
                G.add_vertices(prv_succ, res)
            prv_succ = succ
                
    #if block doesnt have any branch instr
    if head is None:
        head = G.add_nod(l_instr)
        succ = [head]
    #dont forget last instructions of block
    #we can also create a nod with no instr in if l_instr is empty...
    elif l_instr:
        res = G.add_nod(l_instr)
        G.add_vertices(prv_succ, res)
        succ = [res]
    return (head, succ)
                

def compute_block_function(f):
    G = DAG()
    (head, succ) = compute_block_block(f.body, G)
    fun_end = G.add_nod([], False)
    G.add_vertices(succ, fun_end)
    print(str(G))
    G.is_return_defined()
    G.dead_code()
            
FunctionDef.compute_block = compute_block_function


def compute_block_return(instr, G, l_instr):
    ret_nod = G.add_nod(l_instr, True)
    return (ret_nod, [])

Return.compute_block = compute_block_return

def compute_block_if(ifinstr, G, l_instr):
    if_nod = G.add_nod(l_instr)
    (then_nod, then_end) = compute_block_block(ifinstr.body, G)
    
    
    if ifinstr.orelse:
        (else_nod, else_end) = compute_block_block(ifinstr.orelse, G)
        G.add_vertice(if_nod, else_nod)
    else:
        #trick.. 
        else_end = [if_nod]
        
    G.add_vertice(if_nod, then_nod)
    return (if_nod, then_end+else_end)
        
    
If.compute_block = compute_block_if

def compute_block_while(whileinstr, G, l_instr):
    while_nod = G.add_nod(l_instr)
    (body_nod, body_end) = compute_block_block(whileinstr.body, G)
    body_end.append(while_nod)
    G.add_vertice(while_nod, body_nod)
    return (while_nod, body_end)
    
While.compute_block = compute_block_while


def compute_block_for(forinstr, G, l_instr):
    for_nod = G.add_nod(l_instr)
    (body_nod, body_end) = compute_block_block(forinstr.body, G)
    body_end.append(for_nod)
    G.add_vertice(for_nod, body_nod)
    return (for_nod, body_end)
    
While.compute_block = compute_block_while

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