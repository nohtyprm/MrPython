
"""The abstract syntax tree of type expressions."""


class TypeAST:
    def __init__(self, annotation):
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
        raise NotImplementedError("Equality not implemented for this node type (please report)\n  ==> {}".format(self))

    def is_hashable(self):
        raise NotImplementedError("Method is_hashable is abstract")

    def unalias(self, type_defs):
        raise NotImplementedError("Method unalias is abstract")
    
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
        return self
    
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
            raise KeyError("Type alias '{}' not found in type definitions (please report)".format(self.alias_name))

        unaliased_type = type_defs[self.alias_name].unalias(type_defs)
        unaliased_type.alias_name = self.alias_name

        return unaliased_type
    
    def __eq__(self, other):
        return isinstance(other, BoolType)

    def __str__(self):
        return self.alias_name

    def __repr__(self):
        return "TypeAlias({})".format(self.alias_name)
    
    
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
        return self
    
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
        return self

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
        return self

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
        return self

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
        return self

    def __eq__(self, other):
        return isinstance(other, NoneTypeType)

    def __str__(self):
        return "NoneType"

    def __repr__(self):
        return "NoneType()"

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
        return self

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
        return self
    
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
        for elem_type in elem_types:
            if not elem_type.is_hashable():
                return False
        return True

    def size(self):
        return len(self.elem_types)

    def unalias(self, type_defs):
        nelem_types = []
        for elem_type in self.elem_types:
            nelem_types.append(elem_type.unalias(type_defs))
        return TupleType(nelem_types, self.annotation if self.annotated else None)

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

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return ListType(nelem_type, self.annotation)

    def subst(self, type_env):
        return ListType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def unalias(self, type_defs):
        return ListType(self.elem_type.unalias(type_defs), self.annotation if self.annotated else None)

    def __eq__(self, other):
        return isinstance(other, ListType) and other.elem_type == self.elem_type

    def is_hashable(self):
        return False

    def is_emptylist(self):
        return self.elem_type is None

    def __str__(self):
        if self.elem_type:
            return "list[{}]".format(str(self.elem_type))
        else:
            return "emptylist"

    def __repr__(self):
        return "ListType({})".format(repr(self.elem_type))

class SetType(TypeAST):
    def __init__(self, elem_type=None, annotation=None):
        super().__init__(annotation)
        if elem_type is not None and not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def __eq__(self, other):
        return isinstance(other, SetType) and other.elem_type == self.elem_type

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return SetType(nelem_type, self.annotation)

    def susbt(self, type_env):
        return SetType(self.elem_type.subst(type_env), self.annotation)

    def is_hashable(self):
        return False

    def is_emptyset(self):
        return self.elem_type is None

    def unalias(self, type_defs):
        return SetType(self.elem_type.unalias(type_defs), self.annotation if self.annotated else None)

    def __str__(self):
        if self.elem_type:
            return "set[{}]".format(str(self.elem_type))
        else:
            return "emptyset"

    def __repr__(self):
        return "SetType({})".format(repr(self.elem_type))

class DictType(TypeAST):
    def __init__(self, key_type=None, value_type=None, annotation=None):
        super().__init__(annotation)
        if key_type is not None and not isinstance(key_type, TypeAST):
            raise ValueError("Key type is not a TypeAST: {}".format(key_type))
        self.key_type = key_type
        if key_type is None and value_type is not None:
            raise ValueError("Value type must be None because Key Type is: {}".format(value_type))
        if value_type is not None and not isinstance(value_type, TypeAST):
            raise ValueError("Value type is not a TypeAST: {}".format(value_type))
        self.value_type = value_type

    def rename_type_variables(self, rmap):
        nkey_type = self.key_type.rename_type_variables(rmap)
        nvalue_type = self.value_type.rename_type_variables(rmap)
        return DictType(nkey_type, nvalue_type, self.annotation)

    def susbt(self, type_env):
        return DictType(self.key_type.subst(type_env)
                        , self.value_type.subst(type_env)
                        , self.annotation)

    def is_hashable(self):
        return False

    def unalias(self, type_defs):
        return DictType(self.key_type.unalias(type_defs)
                        , self.value_type.unalias(type_defs)
                        , self.annotation if self.annotated else None)

    
    def __eq__(self, other):
        return isinstance(other, DictType) and other.key_type == self.key_type \
            and other.value_type == self.value_type

    def is_emptydict(self):
        return self.key_type is None and self.value_type is None

    def __str__(self):
        if self.key_type:
            return "dict[{}:{}]".format(str(self.key_type), str(self.value_type))
        else:
            return "emptydict"

    def __repr__(self):
        return "DictType({},{})".format(repr(self.key_type), repr(self.value_type))

class IterableType(TypeAST):
    def __init__(self, elem_type, annotation=None):
        super().__init__(annotation)
        if not isinstance(elem_type, TypeAST):
            raise ValueError("Element type is not a TypeAST: {}".format(elem_type))
        self.elem_type = elem_type

    def rename_type_variables(self, rmap):
        nelem_type = self.elem_type.rename_type_variables(rmap)
        return IterableType(nelem_type, self.annotation)

    def susbt(self, type_env):
        return IterableType(self.elem_type.subst(type_env), self.annotation)

    def unalias(self, type_defs):
        return IterableType(self.elem_type.unalias(type_defs), self.annotation if self.annotated else None)

    def is_hashable(self):
        return False

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

    def susbt(self, type_env):
        return SequenceType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def is_hashable(self):
        return False

    def unalias(self, type_defs):
        return SequenceType(self.elem_type.unalias(type_defs), self.annotation if self.annotated else None)

    
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

    def susbt(self, type_env):
        return OptionType(self.elem_type.subst(type_env), self.annotation if self.annotated else None)

    def unalias(self, type_defs):
        return OptionType(self.elem_type.unalias(type_defs), self.annotation if self.annotated else None)
    
    def is_hashable(self):
        return False

    def __eq__(self, other):
        return isinstance(other, OptionType) and other.elem_type == self.elem_type

    def __str__(self):
        return "Option[{}]".format(str(self.elem_type))

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

    def unalias(self, type_defs):
        nparam_types = []
        for param_type in self.param_types:
            nparam_types.append(param_type.unalias(type_defs))
        nret_type = self.ret_type.unalias(type_defs)
        nfntype = FunctionType(nparam_types, self.ret_type, self.partial, self.annotation if self.annotated else None)
        nfntype.ret_type = nret_type
        return nfntype
    
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
