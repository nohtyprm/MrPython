import os.path, sys
import ast
import math
from graph import Digraph
from graph import DepthFirstTraversal

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
    from prog_ast import *
    from type_ast import *
    from type_parser import (type_expression_parser, function_type_parser, var_type_parser, type_def_parser)

    from translate import tr


"""
2 things can be done
-> check for return in all code branches (cannot access a nod with no successor which is not a return (implicit return))
-> check for dead code : identify strong connex components of the graph, rest is dead-code
"""

class FunGraph(Digraph):
    def __init__(self):
        super().__init__()
        self.vertices_info = dict()
    
    def add_vertex(self, vertex):
        super().add_vertex(vertex.get_id())
        self.vertices_info[vertex.get_id()] = vertex
    
    def add_edge(self, src, dest):
        super().add_edge(src.get_id(), dest.get_id())
    
    def add_edges(self, list_src, dest):
        for vertex in list_src:
            super().add_edge(vertex.get_id(), dest.get_id())
    
    def start(self):
        return self.vertices[0]
    
    def vertex_info(self, v_id):
        return self.vertices_info[v_id]
            
    def to_dot(self):
        '''Generates a dot/graphviz representation of
        the directed graph.'''
        return """digraph {{
  {}
  {}
}}""".format("\n  ".join(("{} ;".format(vertex.to_dot()) for vertex in self.vertices_info.values())), 
             "\n  ".join(("{} -> {} ;".format(src, dst)
                          for (src, dsts) in self.edges.items() for dst in dsts)))
    
    

def add_1_generator():
    k = 0
    while True:
        k += 1
        yield k


ident_gen = add_1_generator()
class BasicBlock():
    def __init__(self, l_instr, ret=False):
        self.ret = ret
        self.l_instr = l_instr
        self.ident = next(ident_gen)
        self.voisins = []
    
    def add_voisin(self, v):
        self.voisins.append(v)
    
    def is_return(self):
        return self.ret
    
    def get_id(self):
        return self.ident
    
    def is_implicit_return(self):
        if self.l_instr:
            return False
        return True
        
    def __str__(self):
        s = "[Ret:"
        s += str(self.ret) + ", Voisins:{"
        for v in self.voisins:
            s += str(v) + " "
        s += "}, LInstr : " + str(self.l_instr)+"]"
        return s
    
    def to_dot(self):
        shape = "circle"
        fillcolor = "white"
        if not self.l_instr:
            fillcolor = "red, style = filled"
        if self.ret:
            shape = "doublecircle"
            
        return "{} [shape={} fillcolor={}]".format(self.get_id(), shape, fillcolor)
    
    
class ImplicitReturnReached(Exception):
    pass



class ReturnSearch(DepthFirstTraversal):
    def __init__(self, CFG):
        super().__init__(CFG, CFG.start())
        
    def on_discovered_vertex(self, parent, vertex_id):
        if self.digraph.vertex_info(vertex_id).is_implicit_return():
            raise ImplicitReturnReached("Implicit return is reachable")
            
    def __next__(self):
        if not self.vertex_stack:
            raise StopIteration()
        vertex = self.vertex_stack.pop()
        self.parents.add(vertex)

        for dest in self.digraph.edges.get(vertex, {}):
            self._discover_vertex(vertex, dest)
        
        self.parents.remove(vertex)
        self.on_visited_vertex(vertex)
        return vertex
    
def check_for_return(CFG):
    
    search = ReturnSearch(CFG)
    try:
        for b in search:
            pass
    except ImplicitReturnReached:
        print("Function may not return")
        return False
    return True

class DeadCode(Exception):
    pass
    
class DeadCodeSearch(DepthFirstTraversal):
    def __init__(self, CFG):
        super().__init__(CFG, CFG.start())
        
            
    def __next__(self):
        if not self.vertex_stack:
            #implicit return must be taken into account.. little improvment to do here
            if len(self.undiscovered) <= 1:
                raise StopIteration()
            else:
                raise DeadCode("dead code was detected")
        vertex = self.vertex_stack.pop()
        self.parents.add(vertex)
        
        for dest in self.digraph.edges.get(vertex, {}):
            self._discover_vertex(vertex, dest)

        self.parents.remove(vertex)
        self.on_visited_vertex(vertex)
        return vertex


def check_for_dead_code(CFG):
    
    search = DeadCodeSearch(CFG)
    try:
        for b in search:
            pass
    except DeadCode as e:
        print(str(e))
        return False
    return True

"""
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
        
"""
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
                G.add_edges(prv_succ, res)
            prv_succ = succ
                
    #if block doesnt have any branch instr
    if head is None:
        head = BasicBlock(l_instr)
        G.add_vertex(head)
        succ = [head]
    #dont forget last instructions of block
    #we can also create a nod with no instr in if l_instr is empty...
    elif l_instr:
        res = BasicBlock(l_instr)
        G.add_vertex(res)
        G.add_edges(prv_succ, res)
        succ = [res]
    return (head, succ)
                

cpt_fun = add_1_generator()
def compute_block_function(f):
    G = FunGraph()
    (head, succ) = compute_block_block(f.body, G)
    fun_end = BasicBlock([], False)
    G.add_vertex(fun_end)
    G.add_edges(succ, fun_end)
    os.makedirs("tmp", exist_ok=True)
    fun_ident = next(cpt_fun)
    f = open("tmp/digraph_function_{}.dot".format(fun_ident), "w")
    f.write(G.to_dot())
    f.close()
    check_for_return(G)
    check_for_dead_code(G)
    print(str(G))
    #G.is_return_defined()
    #G.dead_code()
            
FunctionDef.compute_block = compute_block_function


def compute_block_return(instr, G, l_instr):
    ret_v = BasicBlock(l_instr, True)
    G.add_vertex(ret_v)
    return (ret_v, [])

Return.compute_block = compute_block_return

def compute_block_if(ifinstr, G, l_instr):
    if_v = BasicBlock(l_instr)
    G.add_vertex(if_v)
    (then_v, then_end) = compute_block_block(ifinstr.body, G)
    
    
    if ifinstr.orelse:
        (else_v, else_end) = compute_block_block(ifinstr.orelse, G)
        G.add_edge(if_v, else_v)
    else:
        #trick.. 
        else_end = [if_v]
        
    G.add_edge(if_v, then_v)
    return (if_v, then_end+else_end)
        
    
If.compute_block = compute_block_if

def compute_block_while(whileinstr, G, l_instr):
    while_v = BasicBlock(l_instr)
    G.add_vertex(while_v)
    (body_v, body_end) = compute_block_block(whileinstr.body, G)
    G.add_edge(while_v, body_v)
    G.add_edges(body_end, while_v)
    
    
    body_end.append(while_v)
    return (while_v, body_end)
    
While.compute_block = compute_block_while



For.compute_block = compute_block_while


def dag_from_file(filename):
    prog = Program()
    prog.build_from_file(filename)
    prog.visitDAG()
    #ctx = prog.type_check()
    return None


#dag_from_file("tuple-effect.py")

