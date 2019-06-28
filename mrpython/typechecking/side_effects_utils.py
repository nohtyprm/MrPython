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
    from typechecker import *
    
else:
    from .prog_ast import *
    from .type_ast import *
    

class AliasRef:
    def __init__(self, ref, index_in = None, index_out = None):
        self.ref = ref
        if index_in:
            self.index_in = index_in
        else:
            self.index_in = []

        if index_out:
            self.index_out = index_out
        else:
            self.index_out = []

    def access(self, c):
        if self.index_out:
            p = self.index_out.pop()
            if (not self.ref == "*") and c != p:
                raise NotImplementedError("error in side-effect-checking, please report")
        else:
            self.index_in.append(c)

    def unaccess(self, c):
        self.index_out.append(c)

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
            
        return  repr_index_out + str(self.ref) +repr_index_in

    def is_protected(self):
        return self.ref == '*' and not self.index_out
    
    
def alias_expr (expr, ctx):
    return set()
Expr.alias = alias_expr

def get_all_alias_ctx(ctx, var):
    res = set()
    to_add = set([AliasRef(var)])
    while to_add:
        res = res | to_add
        to_add_next = set()
        for alias in to_add:
            #to_add_next = to_add_next | (ctx.get_alias(alias.ref) - res)
            for a in ctx.get_alias(alias.ref):
                a = AliasRef(a.ref, a.index_in + alias.index_in, alias.index_out + a.index_out)
                if not (a in res):
                    to_add_next.add(a)
        to_add = to_add_next
    return res


def alias_var (var, ctx):
    if ctx.in_call:
        res = ctx.get_all_alias(var.name)
        res.add(AliasRef(var.name))
        return res
    
    if isinstance(ctx.local_env.get(var.name), TupleType) or isinstance(ctx.param_env.get(var.name), TupleType):
        return ctx.get_alias(var.name)
    return set([AliasRef(var.name)])

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
            res.add(elt.unaccess(str(i)))
        i = i +1
    return res

ETuple.alias = alias_ETuple


def alias_Indexing(indexing, ctx):
    aliases = indexing.subject.alias(ctx)
    for a in aliases:
        a.access(".")
    return aliases

Indexing.alias = alias_Indexing
    
def side_effect_ECall(call, ctx):
    is_side_effect = False
    if call.fun_name == "append":
        ctx.in_call = True
        aliases_extended = call.receiver.alias(ctx)
        ctx.in_call = False
        aliases_receiver = call.receiver.alias(ctx)

        #variables potentially impacted
        for alias in aliases_extended:
            if alias.is_protected():
                is_side_effect = True
                break;

        #variable actually referenced in expression
        aliases_arg = call.arguments[0].alias(ctx)
        for alias_rec in aliases_receiver:
            tmp = set()
            #if alias_rec.index_out we have a top level copy
            if not alias_rec.index_out:
                for alias_arg in aliases_arg:
                    #to ensure all aliasing links are in form LL->[.]P rather than LL[.]->P
                    alias_index_in = ["."] + alias_rec.index_in + alias_arg.index_out
                    tmp.add(AliasRef(alias_arg.ref, alias_arg.index_in[:], alias_index_in))
                    
                ctx.add_alias(alias_rec.ref, tmp)
    ctx.print_alias()
            
    return is_side_effect




ECall.side_effect = side_effect_ECall

def linearize(ctx, lhs_expr, aliases):
    if isinstance(lhs_expr, LHSVar):
        ctx.replace_alias(lhs_expr.var_name, aliases)
    else:
        for i in range(len(lhs_expr.elements)):
            alias_elem = set()
            for a in aliases:
                if a == AliasRef("*") or a.index_out[0] == str(i):
                    tmp = AliasRef(a.ref, a.index_in[:], a.index_out[:])
                    tmp.access(str(i))
                    alias_elem.add(tmp)
            linearize(ctx, lhs_expr.elements[i], alias_elem)
                            
                               
                               
        

def assign_extended(working_var, working_expr, ctx):
    if isinstance(working_var, LHSVar):
        ctx.replace_alias(working_var.var_name, working_expr.alias(ctx))
    if isinstance(working_var, LHSTuple):
        if (not isinstance(working_expr, ETuple)):
            aliases = ctx.get_alias(working_expr.name)
            linearize(ctx, working_var, aliases)
        else:
            for i in range(len(working_var.elements)):
                assign_extended(working_var.elements[i], working_expr.elements[i], ctx)
        
def side_effect_Assign(assign, ctx):
    assign_extended(assign.target, assign.expr, ctx)
Assign.side_effect = side_effect_Assign


