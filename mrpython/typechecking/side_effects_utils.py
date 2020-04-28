import os.path, sys
import ast
from collections import deque

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
    from typechecker import *

else:
    try:
        from .prog_ast import *
        from .type_ast import *
    except ImportError:
        from prog_ast import *
        from type_ast import *
        
class AliasRef:
    def __init__(self, ref, nb_def, index_in = None, index_out = None):
        self.ref = ref
        self.nb_def = nb_def
        if index_in:
            self.index_in = index_in
        else:
            self.index_in = deque()

        if index_out:
            self.index_out = index_out
        else:
            self.index_out = deque()

    def access(self, c):
        if self.index_out and self.index_out[0] == c:
            p = self.index_out.popleft()
        else:
            self.index_in.append(c)

    def unaccess(self, c):
        self.index_out.appendleft(c)

    def __eq__(self, other):
        return isinstance(other, AliasRef) and self.__repr__() == other.__repr__()

    def __hash__(self):
        return self.__repr__().__hash__()

    def __repr__(self):
        repr_index_out = ""
        repr_index_in = ""
        if self.index_out:
            repr_index_out = "[" + "".join(self.index_out) + "]"
        if self.index_in:
            repr_index_in = "[" + "".join(self.index_in) + "]"

        return  repr_index_out + str(self.ref) + str(self.nb_def) + repr_index_in

    def is_protected(self, ctx):
        return (self.ref in ctx.protected) and not self.index_out


    def simplify(self):
        if self.index_out and self.index_out[0] != ".":
            if self.index_in[len(self.index_in)-1] == self.index_out[0]:
                self.index_in.pop()
                self.index_out.popleft()
                return self.simplify()
            else:
                return None
        return self


def alias_expr (expr, ctx):
    return set()
Expr.alias = alias_expr

def get_all_alias_ctx(ctx, var):
    res = set()
    marked = set()
    to_add = set([AliasRef(var.name, ctx.var_def[var.name])])
    while to_add:
        res = res | to_add
        to_add_next = set()
        for alias in to_add:
            #to_add_next = to_add_next | (ctx.get_alias(alias.ref) - res)
            if alias.ref not in marked:
                marked.add(alias.ref)
                for a in ctx.get_alias(AliasRef(alias.ref, ctx.var_def[alias.ref])):
                    a = AliasRef(a.ref, ctx.var_def[a.ref], concat_deque(a.index_in, alias.index_in), concat_deque(alias.index_out, a.index_out))
                    if not (a in res):
                        to_add_next.add(a)
        to_add = to_add_next

    #for tuples
    final_res = set()
    for alias in res:
        tmp = alias.simplify()
        if tmp:
            final_res.add(tmp)

    return final_res


def alias_var (var, ctx):
    if ctx.in_call:
        res = ctx.get_all_alias(var)
        res.add(AliasRef(var.name, ctx.var_def[var.name]))
        return res

    return set([AliasRef(var.name, ctx.var_def[var.name])])

EVar.alias = alias_var

def alias_EList(lst, ctx):
    res = set()
    for elt in lst.elements:
        res = res | elt.alias(ctx)

    for ref in res:
        ref.unaccess('.')

    return res

EList.alias = alias_EList

def alias_ETuple(tpl, ctx):
    i = 0
    res = set()
    for elt in tpl.elements:
        for a in elt.alias(ctx):
            a.unaccess(str(i))
            res.add(a)
        i = i + 1
    return res

ETuple.alias = alias_ETuple


def alias_Indexing(indexing, ctx):
    aliases = indexing.subject.alias(ctx)
    for a in aliases:
        a.access(".")
    return aliases

Indexing.alias = alias_Indexing

def alias_EAdd(eadd, ctx):
    aliases_l = eadd.left.alias(ctx)
    aliases_r = eadd.right.alias(ctx)
    res = aliases_l | aliases_r

    for a in res:
        a.access(".")
        a.unaccess(".")
    return res
EAdd.alias = alias_EAdd

def alias_Slicing(slc, ctx):
    res = slc.subject.alias(ctx)

    for a in res:
        a.access(".")
        a.unaccess(".")
    return res

Slicing.alias = alias_Slicing

#########################
## python <= 3.4  fixes
def copy_deque(deq):
    ndeque = deque()
    for e in deq:
        ndeque.append(e)
    return ndeque


def concat_deque(deq1, deq2):
    ndeque = copy_deque(deq1)
    for e in deq2:
        ndeque.append(e)
    return ndeque

#########################

def side_effect_ECall(call, ctx):
    is_side_effect = False
    protected_var = set()

    if call.fun_name == "append":
        ctx.in_call = True
        aliases_extended = call.receiver.alias(ctx)
        ctx.in_call = False
        aliases_receiver = call.receiver.alias(ctx)


        #variables potentially impacted

        for alias in aliases_extended:
            if alias.is_protected(ctx):
                is_side_effect = True
                protected_var.add(alias.ref)

        #variable actually referenced in expression
        aliases_arg = call.arguments[0].alias(ctx)
        for alias_rec in aliases_receiver:
            tmp = set()
            #if alias_rec.index_out we have a top level copy
            if not alias_rec.index_out:
                for alias_arg in aliases_arg:
                    #to ensure all aliasing links are in form LL->[.]P rather than LL[.]->P
                    alias_index_in =  concat_deque(alias_rec.index_in, alias_arg.index_out)
                    alias_index_in.appendleft(".")
                    tmp.add(AliasRef(alias_arg.ref, ctx.var_def[alias_arg.ref], copy_deque(alias_arg.index_in), alias_index_in))

                ctx.add_alias(alias_rec.ref, tmp)

    elif  call.fun_name == "add":
        ctx.in_call = True
        aliases_extended = call.receiver.alias(ctx)
        ctx.in_call = False
        #variables potentially impacted
        for alias in aliases_extended:
            if alias.is_protected(ctx):
                is_side_effect = True
                protected_var.add(alias.ref)

    return (is_side_effect, protected_var)




ECall.side_effect = side_effect_ECall

def linearize(ctx, lhs_expr, aliases):
    if isinstance(lhs_expr, LHSVar):
        ctx.add_var_def(lhs_expr.var_name)
        ctx.add_alias(lhs_expr.var_name, aliases)
    else:
        for i in range(len(lhs_expr.elements)):
            alias_elem = set()
            for a in aliases:
                tmp = AliasRef(a.ref, ctx.var_def[a.ref], copy_deque(a.index_in), copy_deque(a.index_out))
                tmp.access(str(i))
                alias_elem.add(tmp)
            linearize(ctx, lhs_expr.elements[i], alias_elem)


def assign_extended(ctx, working_var, working_expr, suffix):
    if isinstance(working_var, LHSVar):
        ctx.add_var_def(working_var.var_name)
        aliases = working_expr.alias(ctx)
        for a in aliases:
            for s in suffix:
                a.access(s)
        ctx.add_alias(working_var.var_name, aliases)

    if isinstance(working_var, LHSTuple):
        if (not isinstance(working_expr, ETuple)):
            aliases = working_expr.alias(ctx)
            linearize(ctx, working_var, aliases)
        else:
            for i in range(len(working_var.elements)):
                assign_extended(ctx, working_var.elements[i], working_expr.elements[i], suffix)

def side_effect_Assign(assign, ctx):
    assign_extended(ctx, assign.target, assign.expr, "")

Assign.side_effect = side_effect_Assign

def side_effect_For(efor, ctx):
    assign_extended(ctx,efor.target, efor.iter, ".")

For.side_effect = side_effect_For
