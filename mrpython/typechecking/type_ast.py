
"""The abstract syntax tree of type expressions."""
import math

class TypeAST:
    
    def __init__(self, annotation):
        self.flag = False
        self.flag_lvl = 0
        if annotation:
            self.annotated=True
            self.annotation=annotation
        else:
            self.annotated=False

    def rename_type_variables(self, rmap):
        raise NotImplementedError("Type variable renaming not implemented for this node type (please report)\n  ==> {}".format(self))

    def subst(self, type_env):
        raise NotImplementedError("Substitution not implemented for this node type (please report)\n  ==> {}".format(self))

    def __eq__(self, other):
        if (other == None):
            return False
        raise NotImplementedError("Equality not implemented for this node type (please report)\n  ==> {}".format(self))

    def is_hashable(self):
        raise NotImplementedError("Method is_hashable is abstract")

    def fetch_unhashable(self):
        return None

    def unalias(self, type_defs):
        raise NotImplementedError("Method unalias is abstract")
        
    def raise_flag(self):
        """do nothing ..."""
    
    def get_flag_lvl(self):
        return math.inf +1
    
    def get_flag(self):
        return self.flag
    
class Anything(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return False

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)
    
    def __eq__(self, other):
        return isinstance(other, Anything)

    def __str__(self):
        return "any"

    def __repr__(self):
        return "Anything()"

class TypeAlias(TypeAST):
    def __init__(self, alias_name, annotation=None):
        super().__init__(annotation)
        self.alias_name = alias_name

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        if self.alias_name not in type_defs:
            return (None, self.alias_name)

        unaliased_type, unknown_alias = type_defs[self.alias_name].unalias(type_defs)
        if unaliased_type is None:
            return (None, unknown_alias)
        unaliased_type.alias_name = self.alias_name

        return (unaliased_type, None)
    
    def __eq__(self, other):
        return isinstance(other, BoolType)

    def __str__(self):
        return self.alias_name

    def __repr__(self):
        return "TypeAlias({})".format(self.alias_name)
    
class FileType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)
    
    def __eq__(self, other):
        return isinstance(other, FileType)

    def __str__(self):
        return "FILE"

    def __repr__(self):
        return "FileType()"
    

class BoolType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)
    
    def __eq__(self, other):
        return isinstance(other, BoolType)

    def __str__(self):
        return "bool"

    def __repr__(self):
        return "BoolType()"

class IntType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)

    def __eq__(self, other):
        return isinstance(other, IntType)

    def __str__(self):
        return "int"

    def __repr__(self):
        return "IntType()"

class FloatType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)

    def __eq__(self, other):
        return isinstance(other, FloatType)

    def __str__(self):
        return "float"

    def __repr__(self):
        return "FloatType()"


class NumberType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)

    def __eq__(self, other):
        return isinstance(other, NumberType)

    def __str__(self):
        return "Number"

    def __repr__(self):
        return "NumberType()"


class NoneTypeType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)

    def __eq__(self, other):
        return isinstance(other, NoneTypeType)

    def __str__(self):
        return "NoneType"

    def __repr__(self):
        return "NoneType()"

class ImageType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)

    def is_hashable(self):
        return True

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def unalias(self, type_defs):
        return (self, None)

    def __eq__(self, other):
        return isinstance(other, ImageType)

    def __str__(self):
        return "Image"

    def __repr__(self):
        return "ImageType()"

    
class StrType(TypeAST):
    def __init__(self, annotation=None):
        super().__init__(annotation)
        #self.elem_type = StrType() # how strange !

    def __eq__(self, other):
        return isinstance(other, StrType)

    def rename_type_variables(self, rmap):
        return self

    def subst(self, type_env):
        return self

    def is_hashable(self):
        return True

    def unalias(self, type_defs):
        return (self, None)

    def __str__(self):
        return "str"

    def __repr__(self):
        return "StrType()"


class TypeVariable(TypeAST):
    def __init__(self, var_name, annotation=None):
        super().__init__(annotation)
        if not isinstance(var_name, type("")):
            raise ValueError("Type variable name is not a string: {}".format(var_name))
        self.var_name = var_name

    def __eq__(self, other):
        return isinstance(other, TypeVariable) and other.var_name == self.var_name

    def rename_type_variables(self, rmap):
        if self.var_name in rmap:
            return rmap[self.var_name]
        else:
            nvar = TypeVariable('_{}'.format(len(rmap)+1), self.annotation)
            rmap[self.var_name] = nvar
            return nvar

    def subst(self, type_env):
        if self.var_name in type_env:
            return type_env[self.var_name]
        else:
            return self

    def is_hashable(self):
        return True

    def is_call_variable(self):
        if self.var_name.startswith('_'):
            return True
        else:
            return False

    def unalias(self, type_defs):
        return (self, None)
    
    def __str__(self):
        return '_' if self.var_name.startswith('_') else self.var_name

    def __repr__(self):
        return 'TypeVariable({})'.format(self.var_name)

class TupleType(TypeAST):
    def __init__(self, elem_types, annotation=None):
        super().__init__(annotation)
        if len(elem_types) == 0:
            raise ValueError("Empty tuple type not allowed in Python101")
        for elem_type in elem_types:
            if not isinstance(elem_type, TypeAST):
                raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_types = elem_types

    def raise_flag(self):
        self.flag = True
        for elem_type in self.elem_types:
            elem_type.raise_flag()
    
    def get_flag(self):
        return self.flag
    
    def set_flag_lvl(self, val):
        self.flag_lvl = val
    
    def get_flag_lvl(self):
        return self.flag_lvl
    

    def rename_type_variables(self, rmap):
        nelem_types = []
        for elem_type in self.elem_types:
            nelem_types.append(elem_type.rename_type_variables(rmap))
        return TupleType(nelem_types, self.annotation if self.annotated else None)

    def subst(self, type_env):
        nelem_types = []
        for elem_type in self.elem_types:
            nelem_types.append(elem_type.subst(type_env))
        return TupleType(nelem_types, self.annotation if self.annotated else None)

    def is_hashable(self):
        for elem_type in self.elem_types:
            if not elem_type.is_hashable():
                return False
        return True

    def fetch_unhashable(self):
        for elem_type in self.elem_types:
            result = elem_type.fetch_unhashable()
            if result is not None:
                return result

        return None
    
    def size(self):
        return len(self.elem_types)

    def unalias(self, type_defs):
        nelem_types = []
        for elem_type in self.elem_types:
            uelem_type, unknown_alias = elem_type.unalias(type_defs)
            if uelem_type is None:
                return (None, unknown_alias)
            
            nelem_types.append(uelem_type)
            
        return (TupleType(nelem_types, self.annotation if self.annotated else None)
                , None)

    def __str__(self):
        return "tuple[{}]".format(",".join((str(et) for et in self.elem_types)))

    def __repr__(self):
        return "TupleType([{}])".format(",".join((repr(et) for et in self.elem_types)))

class ListType(TypeAST):
    def __init__(self, elem_type=None, annotation=None):
        super().__init__(annotation)
        if elem_type is not None and not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type
    
    #flag all suboccurences
    def raise_flag(self):
        self.flag = True
        self.elem_type.raise_flag()
    
    def get_flag(self):
        return self.flag
    
    def set_flag_lvl(self, val):
        self.flag_lvl = val
    
    def get_flag_lvl(self):
        return self.flag_lvl
    
    

    def rename_type_variables(self, rmap):
        if self.elem_type is None:
            return self

        nelem_type = self.elem_type.rename_type_variables(rmap)
        return ListType(nelem_type, self.annotation)

    def subst(self, type_env):
        if self.elem_type is None:
            return self
        return ListType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def unalias(self, type_defs):
        uelem_type, unknown_alias = self.elem_type.unalias(type_defs)
        if uelem_type is None:
                return (None, unknown_alias)
        return (ListType(uelem_type, self.annotation if self.annotated else None)
                , None)

    def __eq__(self, other):
        return isinstance(other, ListType) and other.elem_type == self.elem_type

    def is_hashable(self):
        return False

    def fetch_unhashable(self):
        if self.elem_type is None:
            return None
        result = self.elem_type.fetch_unhashable()
        if result is not None:
            return result

        return None
    
    def is_emptylist(self):
        return self.elem_type is None

    def __str__(self):
        if self.elem_type:
            return "list[{}]".format(str(self.elem_type))
        else:
            return "emptylist"

    def __repr__(self):
        return "ListType({})".format(repr(self.elem_type)) if self.elem_type else "ListType()"

class SetType(TypeAST):
    def __init__(self, elem_type=None, annotation=None):
        super().__init__(annotation)
        if elem_type is not None and not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def __eq__(self, other):
        return isinstance(other, SetType) and other.elem_type == self.elem_type

    def rename_type_variables(self, rmap):
        if self.elem_type is None:
            return self

        nelem_type = self.elem_type.rename_type_variables(rmap)
        return SetType(nelem_type, self.annotation)

    def subst(self, type_env):
        if self.elem_type is None:
            return self
        return SetType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def is_emptyset(self):
        return self.elem_type is None

    def is_hashable(self):
        return False

    def fetch_unhashable(self):
        if self.elem_type is None:
            return None  # has no unhashable
        
        result = self.elem_type.fetch_unhashable()
        if result is not None:
            return result

        if not self.elem_type.is_hashable():
            return self # found a non-hashable set

        return None
    
    def unalias(self, type_defs):
        uelem_type, unknown_alias = self.elem_type.unalias(type_defs)
        if uelem_type is None:
                return (None, unknown_alias)
        return (SetType(uelem_type, self.annotation if self.annotated else None)
                , None)

    def __str__(self):
        if self.elem_type:
            return "set[{}]".format(str(self.elem_type))
        else:
            return "emptyset"

    def __repr__(self):
        return "SetType({})".format(repr(self.elem_type))
    
class DictType(TypeAST):
    def __init__(self, key_type=None, val_type=None, annotation=None):
        super().__init__(annotation)
        if key_type is not None and not isinstance(key_type, TypeAST):
            raise ValueError("Key type is not a TypeAST: {}".format(key_type))
        self.key_type = key_type
        if key_type is None and val_type is not None:
            raise ValueError("Value type must be None because Key Type is: {}".format(val_type))
        if val_type is not None and not isinstance(val_type, TypeAST):
            raise ValueError("Value type is not a TypeAST: {}".format(val_type))
        self.val_type = val_type

    def raise_flag(self):
        self.flag = True
        self.key_type.raise_flag()
        self.val_type.raise_flag()
    
    def get_flag(self):
        return self.flag
    
    def set_flag_lvl(self, val):
        self.flag_lvl = val
    
    def get_flag_lvl(self):
        return self.flag_lvl
    

    def rename_type_variables(self, rmap):
        if self.key_type is None:
            return self
        
        nkey_type = self.key_type.rename_type_variables(rmap)
        nval_type = self.val_type.rename_type_variables(rmap)
        return DictType(nkey_type, nval_type, self.annotation)

    def subst(self, type_env):
        if self.key_type is None:
            return self
        
        return DictType(self.key_type.subst(type_env)
                        , self.val_type.subst(type_env)
                        , self.annotation)

    def is_hashable(self):
        return False
    
    def fetch_unhashable(self):
        if self.key_type is None:
            return None # no unhashable in an empty dictionary
        
        result = self.key_type.fetch_unhashable()
        if result is not None:
            return result

        result = self.val_type.fetch_unhashable()
        if result is not None:
            return result

        if not self.key_type.is_hashable():
            return self # dictionary has unhashable keys
        
        return None        

    def unalias(self, type_defs):
        if self.key_type is None:
            return (self, None)
        
        ukey_type, unknown_alias = self.key_type.unalias(type_defs)
        if ukey_type is None:
            return (None, unknown_alias)
        uval_type, unknown_alias = self.val_type.unalias(type_defs)
        if uval_type is None:
            return (None, unknown_alias)

        return (DictType(ukey_type, uval_type
                         , self.annotation if self.annotated else None)
                , None)

    
    def __eq__(self, other):
        return isinstance(other, DictType) and other.key_type == self.key_type \
            and other.val_type == self.val_type

    def is_emptydict(self):
        return self.key_type is None and self.val_type is None

    def __str__(self):
        if self.key_type:
            return "dict[{}:{}]".format(str(self.key_type), str(self.val_type))
        else:
            return "emptydict"

    def __repr__(self):
        return "DictType({},{})".format(repr(self.key_type), repr(self.val_type))

class IterableType(TypeAST):
    def __init__(self, elem_type, annotation=None):
        super().__init__(annotation)
        if not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return IterableType(nelem_type, self.annotation)

    def subst(self, type_env):
        return IterableType(self.elem_type.subst(type_env), self.annotation)

    def unalias(self, type_defs):
        uelem_type, unknown_alias = self.elem_type.unalias(type_defs)
        if uelem_type is None:
            return (None, unknown_alias)
        return (IterableType(uelem_type, self.annotation if self.annotated else None)
                , None)

    def is_hashable(self):
        return False

    def fetch_unhashable(self):
        result = self.elem_type.fetch_unhashable()
        if result is not None:
            return result

        return None

    def __eq__(self, other):
        return isinstance(other, IterableType) and other.elem_type == self.elem_type

    def __str__(self):
        return "Iterable[{}]".format(str(self.elem_type))

    def __repr__(self):
        return "IterableType({})".format(repr(self.elem_type))

class SequenceType(TypeAST):
    def __init__(self, elem_type, annotation=None):
        super().__init__(annotation)
        if not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return SequenceType(nelem_type, self.annotation)

    def subst(self, type_env):
        return SequenceType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def is_hashable(self):
        return False

    def fetch_unhashable(self):
        result = self.elem_type.fetch_unhashable()
        if result is not None:
            return result

        return None

    def unalias(self, type_defs):
        uelem_type, unknown_alias = self.elem_type.unalias(type_defs)
        if uelem_type is None:
                return (None, unknown_alias)

        return (SequenceType(uelem_type, self.annotation if self.annotated else None)
                , None)

    
    def __eq__(self, other):
        return isinstance(other, SequenceType) and other.elem_type == self.elem_type

    def __str__(self):
        return "Sequence[{}]".format(str(self.elem_type))

    def __repr__(self):
        return "SequenceType({})".format(repr(self.elem_type))

class OptionType(TypeAST):
    def __init__(self, elem_type, annotation=None):
        super().__init__(annotation)
        if not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return OptionType(nelem_type, self.annotation if self.annotated else None)

    def subst(self, type_env):
        return OptionType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def unalias(self, type_defs):
        uelem_type, unknown_alias = self.elem_type.unalias(type_defs)
        if uelem_type is None:
                return (None, unknown_alias)

        return (OptionType(uelem_type, self.annotation if self.annotated else None)
                , None)
    
    def is_hashable(self):
        return self.elem_type.is_hashable()

    def fetch_unhashable(self):
        result = self.elem_type.fetch_unhashable()
        if result is not None:
            return result

        return None
    
    def __eq__(self, other):
        return isinstance(other, OptionType) and other.elem_type == self.elem_type

    def __str__(self):
        return "{} + NoneType".format(str(self.elem_type))

    def __repr__(self):
        return "OptionType({})".format(repr(self.elem_type))

class FunctionType:
    def __init__(self, param_types, ret_type, partial=False, annotation=None):
        if annotation:
            self.annotated=True
            self.annotation=annotation
        else:
            self.annotated=False

        for param_type in param_types:
            if not isinstance(param_type, TypeAST):
                raise ValueError("Parameter type is not a TypeAST: {}".format(param_type))
        self.param_types = param_types

        if not isinstance(ret_type, TypeAST):
            raise ValueError("Return type is not a TypeAST: {}".format(ret_type))

        if partial:
            self.ret_type = OptionType(ret_type)
        else:
            self.ret_type = ret_type

        self.partial = partial

    def rename_type_variables(self, rmap):
        nparam_types = []
        for param_type in self.param_types:
            nparam_types.append(param_type.rename_type_variables(rmap))
        nret_type = self.ret_type.rename_type_variables(rmap)
        nfntype = FunctionType(nparam_types, self.ret_type, self.partial, self.annotation if self.annotated else None)
        nfntype.ret_type = nret_type
        return nfntype

    def subst(self, type_env):
        raise ValueError("No substitution for function types (please report)")

    def fetch_unhashable(self):
        for param_type in self.param_types:
            result = param_type.fetch_unhashable()
            if result is not None:
                return result

        result = self.ret_type.fetch_unhashable()
        if result is not None:
            return result

        return None

    def unalias(self, type_defs):
        nparam_types = []
        for param_type in self.param_types:
            uparam_type, unknown_alias = param_type.unalias(type_defs)
            if uparam_type is None:
                return (None, unknown_alias)
            else:
                nparam_types.append(uparam_type)

        nret_type, unknown_alias = self.ret_type.unalias(type_defs)
        if nret_type is None:
            return (None, unknown_alias)
        
        nfntype = FunctionType(nparam_types, self.ret_type, self.partial, self.annotation if self.annotated else None)
        nfntype.ret_type = nret_type
        return (nfntype, None)
    
    def __str__(self):
        return "{} -> {}".format(" * ".join((str(pt) for pt in self.param_types))
                                 , "{}{}".format(str(self.ret_type if not self.partial else self.ret_type.elem_type), " + NoneType" if self.partial else ""))

    def __repr__(self):
        return "FunctionType([{}], {})".format(", ".join((repr(pt) for pt in self.param_types))
                                               , "{}, {}".format(repr(self.ret_type), "True" if self.partial else "False"))

if __name__ == "__main__":
    print("## Type constructions")

    print("----")
    tup1 = TupleType([BoolType(), IntType(), TypeVariable('α')])
    print(tup1)
    print(repr(tup1))

    print("----")
    list1 = ListType(TypeVariable('β'))
    print(list1)
    print(repr(list1))

    print("----")
    set1 = SetType(TypeVariable('β'))
    print(set1)
    print(repr(set1))

    print("----")
    list2 = ListType(tup1)
    print(list2)
    print(repr(list2))

    print("----")
    set2 = SetType(tup1)
    print(set2)
    print(repr(set2))

    print("----")
    list3 = ListType()
    print(list3)
    print(repr(list3))

    print("----")
    set3 = SetType()
    print(set3)
    print(repr(set3))

    print("----")
    tup2 = TupleType([list2, list1, tup1])
    print(tup2)
    print(repr(tup2))

    print("----")
    dict1 = DictType(StrType(), IntType())
    print(dict1)
    print(repr(dict1))

    print("----")
    dict2 = DictType(tup1, list1)
    print(dict2)
    print(repr(dict2))

    print("----")
    dict3 = DictType()
    print(dict3)
    print(repr(dict3))

    print("----")
    iter1 = IterableType(TypeVariable('β'))
    print(iter1)
    print(repr(iter1))

    print("----")
    iter2 = IterableType(tup1)
    print(iter2)
    print(repr(iter2))

    print("----")
    fun1 = FunctionType([NumberType(), IntType()], FloatType())
    print(fun1)
    print(repr(fun1))

    print("----")
    pfun1 = FunctionType([NumberType(), IntType()], FloatType(), partial=True)
    print(pfun1)
    print(repr(pfun1))
