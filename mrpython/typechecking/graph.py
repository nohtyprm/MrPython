
import os.path, sys
import ast
import math

# coding: utf-8

# # Directed Graphs

# This document provides basic informations about *directed graphs* -- or *digraphs*. A small but useful Python library is built along the way.

# ## 1. Definition and representation

# A *digraph* is a pair $G = \langle V, E \rangle$ with :
#     
#  - $V$ a set of *vertices*
#  
#  - $E \subseteq V \times V$ a set of *edges*
#    
# In Python a digraph can be represented by a list for the vertices and a dictionnary for the edges.
# 
# **Remark** : we could use a set for the vertices -- or even only rely on the `edges` dictionnary -- but it is better to have a portably deterministic way of iterating vertices.

# In[1]:



class Digraph:
    '''Representation of directed graphs.'''
    def __init__(self):
        '''Create an empty graph.'''
        self.vertices = []  # a list for deterministic traversal
        self.edges = dict() # type dict[vertex:list[vertex]]
        
    def add_vertex(self, vertex_id):
        '''Add a vertex labelled as `vertex_id`.
        Precondition : `vertex_id` is not already existing.'''
        self.vertices.append(vertex_id)
        return self
    
    def add_edge(self, src, dst):
        '''Add an edge from vertex `src` to vertex `dst`.
        Precondition : `src` and `dst` reference existing vertices.'''
        src_edges = self.edges.get(src, [])
        src_edges.append(dst)
        self.edges[src] = src_edges
        return self
    
    class IntegrityError(Exception):
        pass
    
    def check_integrity(self):
        '''Check the integrity of the representation.
        *Warning*: the integrity check is costly, use
         only for testing purpose.'''
        
        # check there is no repeated vertex
        freqs = dict()
        max_freq = 0
        max_vertex = None
        for vertex in self.vertices:
            freq = freqs.get(vertex, None)
            if freq is None:
                freq = 1
            else:
                freq += 1
                
            if freq > max_freq:
                max_freq = freq
                max_vertex = vertex
                
            freqs[vertex] = freq
    
        if max_freq > 1:
            raise Digraph.IntegrityError("Vertex '{}' repeated {} times in digraph"                                 .format(max_vertex, max_freq))
            
        # check all edges reference registered vertices
        for (src, dsts) in self.edges:
            if src not in self.vertices:
                raise Digraph.IntegrityError("Vertex '{}' is not registered".format(src))
                dsts_set = set()  # for repetition checking
            for dst in dsts:
                if dst not in self.vertices:
                    raise Digraph.IntegrityError("Vertex '{}' is not registered".format(src))
                if dst in dsts_set:
                    raise Digraph.IntegrityError("Vertex '{}' is repeated in edges".format(dst))
                dsts_set.add(dst)
    
    def to_dot(self):
        '''Generates a dot/graphviz representation of
        the directed graph.'''
        return """digraph {{
  {}
  {}
}}""".format("\n  ".join(("{} ;".format(vertex) for vertex in self.vertices)), 
             "\n  ".join(("{} -> {} ;".format(src, dst)
                          for (src, dsts) in self.edges.items() for dst in dsts)))


# Consider the following *digraph* :

# In[2]:


digraph_ex1 = Digraph().add_vertex('A').add_vertex('B').add_vertex('C').add_vertex('D')    .add_edge('A', 'B')    .add_edge('B', 'C')    .add_edge('C', 'A')    .add_edge('A', 'D')    .add_edge('C', 'D')


# Its graphical representation is as follows.

# In[6]:


#digraph_ex1.show()


# The vertices of the graphs are as follows.

# In[4]:


#digraph_ex1.vertices


# And its edges are given by the following dictionary.

# In[4]:


#digraph_ex1.edges


# Here is another example :

# In[11]:


def Digraph_add_vertices(graph, prefix, nb):
    for k in range(1, nb + 1):
        graph.add_vertex("{}{}".format(prefix, k))
        
    return graph

Digraph.add_vertices = Digraph_add_vertices


# In[12]:


digraph_ex2 = Digraph().add_vertices('N', 9)    .add_edge('N1', 'N3')    .add_edge('N2', 'N4')    .add_edge('N3', 'N5')    .add_edge('N1', 'N6')    .add_edge('N4', 'N6')    .add_edge('N6', 'N5')    .add_edge('N6', 'N9')    .add_edge('N5', 'N7')    .add_edge('N5', 'N8')


# In[13]:


#digraph_ex2.show()


# In[14]:


def digraph_to_svg(graph, dot_path='dot'):
    def find_tempfilename(prefix="digraph_", suffix=".dot"):
        for i in range(99999):
            filename = "{}{}{}".format(prefix, i, suffix)
            try:
                f = open(filename, 'r')
                f.close()
            except OSError:
                return filename
            
    dot_filename = find_tempfilename()
    
    with open(dot_filename, 'w') as dot_file:
        dot_file.write(graph.to_dot())
        
    svg_filename = dot_filename + '.svg'
           
    import subprocess
    ret_code = subprocess.check_call("{dot_path} -Tsvg {dot_filename} -o {svg_filename}".format(**locals()), shell=True)
        
    svg_ret = ""
    with open(svg_filename, 'r') as svg_file:
            svg_ret = svg_file.read()
            
    import os
    os.remove(dot_filename)
    os.remove(svg_filename)
        
    return svg_ret

def show_digraph(graph):
    import IPython.display
    return IPython.display.SVG(digraph_to_svg(graph))

Digraph.show = show_digraph
Digraph.show.__doc__ = "Generates an SVG representation of the graph."


# ### 1.2. Basic operations

# The *roots* of a digraph are the vertices without incoming edges.

# In[15]:


def vertices_with_incoming_edge(graph):
    verts = set()
        
    for (_, dests) in graph.edges.items():
        verts.update(dests)
            
    return verts


# In[16]:


#vertices_with_incoming_edge(digraph_ex1)


# In[17]:


#vertices_with_incoming_edge(digraph_ex2)


# In[18]:


def Digraph_roots(graph):    
    roots = []
    not_roots = vertices_with_incoming_edge(graph)
    for vertex in graph.vertices:
        if vertex not in not_roots:
            roots.append(vertex)
    return roots

Digraph.roots = Digraph_roots


# In[19]:


#digraph_ex1.roots()


# In[20]:


#digraph_ex2.roots()


# ## 2. Graph traversals

# A *graph traversal* is a way of visiting all the vertices of the graph exactly *once* by following the edges. Among the various possible traversals we can distinguish :
# 
#   - *depth-first search* -- or DFS
#   
#   - *breath-first search* -- or BFS
#   

# ### 2.1. Depth-first search

# In[21]:


class DepthFirstTraversal:
    def __init__(self, digraph, init_vertex=None):
        self.digraph = digraph
        
        #{ 
        #
        # **Undiscovered vertices**
        #
        # we use an ordered dictionnary to simulate
        # an set whose elements are ordered accoring
        # to their insertion. This is to ensure the
        # traversal is deterministic
        #}
        import collections
        self.undiscovered = collections.OrderedDict() 
        for v in self.digraph.vertices:
            self.undiscovered[v] = True  # everything undiscovered
            
        #{
        # ** Vertex stack**
        #
        # The depth-first traversal is governed by a
        # stack of vertices to visit.
        #}
        self.vertex_stack = []
        self.parents = set()
               
        #{
        # We begin the traversal by `init_vertex`, or set
        # it to the first vertex found in the graph.
        # }
        if self.digraph.vertices:  # only if there is at least one vertex
            if init_vertex is None:
                init_vertex = self.digraph.vertices[0]
             
            self._discover_vertex(None, init_vertex)
            
            
    def _discover_vertex(self, parent, vertex):
        if vertex in self.undiscovered:
            self.on_forward_edge(parent, vertex)
            self.on_discovered_vertex(parent, vertex)
            del self.undiscovered[vertex]
        
            self.vertex_stack.append(vertex)
            
        elif vertex in self.parents:
            self.on_backward_edge(parent, vertex)
        else:
            self.on_cross_edge(parent, vertex)
            
    def __iter__(self):
        return self
    
    def on_discovered_vertex(self, parent, vertex):
        pass  # subclass for processing upon discovering
    
    def on_visited_vertex(self, vertex):
        pass  # subclass for processing after visiting
    
    def on_forward_edge(self, src, dest):
        pass
    
    def on_backward_edge(self, src, dest):
        pass
    
    def on_cross_edge(self, src, dest):
        pass
    
    def __next__(self):
        if not self.vertex_stack:
            self.parents = set()  # jump
            if not self.undiscovered:
                raise StopIteration()
            def take_first():
                for vertex in self.undiscovered:
                    return vertex
                
            vertex = take_first()
            self._discover_vertex(None, vertex)
            
        vertex = self.vertex_stack.pop()
        self.parents.add(vertex)

        for dest in self.digraph.edges.get(vertex, {}):
            print("DFS: Discover vertex {} from {}".format(dest, vertex))
            print("   ==> parents={}".format(self.parents))
            print("   ==> stack={}".format(self.vertex_stack))
            self._discover_vertex(vertex, dest)
        
        self.parents.remove(vertex)
        self.on_visited_vertex(vertex)
        return vertex


# In[22]:


def depth_first_search(digraph):
    
    dfs = DepthFirstTraversal(digraph)
    
    for vertex in dfs:
        yield vertex
    
Digraph.dfs = depth_first_search


# In[23]:


#[vertex for vertex in digraph_ex1.dfs()]


# In[24]:


#[vertex for vertex in digraph_ex2.dfs()]


# ### 2.2. Breath-first search

# In[25]:


def breath_first_search(digraph):
    if not digraph.vertices:
        return
    
    import collections
    vertex_queue = collections.deque()
    vertex_queue.appendleft(digraph.vertices[0])
    to_visit = collections.OrderedDict()  # used as an ordered set
    for v in digraph.vertices:
        to_visit[v] = True  
    
    while vertex_queue:
        vertex = vertex_queue.pop()
        if vertex in to_visit:
            del to_visit[vertex]
        for dst in digraph.edges.get(vertex, []):
            if dst in to_visit:
                vertex_queue.appendleft(dst)
                
        yield vertex
        
        # special case : if stack is empty
        # but there are other vertices to visit
        if not vertex_queue and to_visit:
            def take_first():
                for vertex in to_visit:
                    return vertex
                
            vertex_queue.appendleft(take_first())
            
    # traversal done
    
Digraph.bfs = breath_first_search


# In[26]:


#[vertex for vertex in digraph_ex1.bfs()]


# In[27]:


#[vertex for vertex in digraph_ex2.bfs()]


# ## 3. Acyclicity

# The sub-category of *directed acyclic graphs*, or *DAG*'s is of particular interest. It is tightly related to the *partially ordered sets* (see the dedicated notebook).
# 
# 

# In[28]:


def digraph_is_cyclic(digraph):
    
    class DFSCycle(DepthFirstTraversal):
        def __init__(self, digraph):
            super().__init__(digraph)
            self.cyclic = False
            
        def on_backward_edge(self, parent, vertex):
            print("cycle detected: {} -> {}".format(parent, vertex))
            self.cyclic = True
    
    check_cycle = DFSCycle(digraph)
    
    for _ in check_cycle:
        pass
    
    return check_cycle.cyclic
        
Digraph.is_cyclic = digraph_is_cyclic




# In[29]:


#digraph_ex1.is_cyclic()


# In[30]:


#digraph_ex2.is_cyclic()
