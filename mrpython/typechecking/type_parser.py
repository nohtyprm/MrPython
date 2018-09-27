
'''The parser for types'''

import os.path, sys

import re

pop_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
#print("pop path=", pop_path)
sys.path.append(pop_path)


from popparser import (Grammar, tokens, parsers, expr, ParseResult)
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer

try:
    from .type_ast import *
except ImportError:
    from type_ast import *

def type_tokenizer():
    tokenizer = Tokenizer()

    # punctuation
    tokenizer.add_rule(tokens.Char('comma', ','))
    tokenizer.add_rule(tokens.Char('open_bracket', '['))
    tokenizer.add_rule(tokens.Char('close_bracket', ']'))


    # spaces
    tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r'))
    tokenizer.add_rule(tokens.Char('newline', '\n'))
    
    # symbols
    tokenizer.add_rule(tokens.Literal('arrow', "->"))
    tokenizer.add_rule(tokens.Literal('expr', "**"))
    tokenizer.add_rule(tokens.Literal('mult', '*'))
    tokenizer.add_rule(tokens.Char('add', '+'))
    tokenizer.add_rule(tokens.Char('pow', '^'))

    # basic types
    tokenizer.add_rule(tokens.Literal('bool_type', 'bool'))
    tokenizer.add_rule(tokens.Literal('int_type', 'int'))
    tokenizer.add_rule(tokens.Literal('float_type', 'float'))
    tokenizer.add_rule(tokens.Literal('Number_type', 'Number'))
    tokenizer.add_rule(tokens.Literal('NoneType_type', 'NoneType'))
    tokenizer.add_rule(tokens.Literal('Image_type', 'Image'))
    tokenizer.add_rule(tokens.Literal('str_type', 'str'))

    tokenizer.add_rule(tokens.Literal('Anything_type', 'Ω'))

    # compound types
    tokenizer.add_rule(tokens.Literal('Iterable_type', 'Iterable'))
    tokenizer.add_rule(tokens.Literal('Sequence_type', 'Sequence'))
    tokenizer.add_rule(tokens.LiteralSet('list_type', 'list', 'List'))
    tokenizer.add_rule(tokens.LiteralSet('set_type', 'set', 'Set'))
    tokenizer.add_rule(tokens.LiteralSet('dict_type', 'dict', 'Dict'))
    tokenizer.add_rule(tokens.LiteralSet('tuple_type', 'tuple', 'Tuple'))

    # type variables
    tokenizer.add_rule(tokens.LiteralSet('type_var'
                                         ,  "α", "alpha", "Alpha", "ALPHA"
                                         , "β", "beta", "Beta", "BETA"
                                         , "γ", "gamma", "Gamma", "GAMMA"
                                         , "δ", "delta", "Delta", "DELTA"
                                         , "η", "eta", "Eta", "ETA"
                                         , "ι", "iota", "Iota", "IOTA"
                                         , "ε", "epsilon", "Epsilon", "EPSILON"
                                         , "ρ", "rho", "Rho", "RHO"))

    # naturals
    tokenizer.add_rule(tokens.Regexp('natural', "[1-9][0-9]*"))
    
    # identifiers
    tokenizer.add_rule(tokens.Regexp('identifier',
                                     "[a-zA-Z_][a-zA-Z_0-9]*'*"))
    
    return tokenizer

def build_typeexpr_grammar(grammar=None):
    if grammar is None:
        grammar = Grammar()

    grammar.register('spaces', parsers.Repeat(parsers.Token('space'), minimum=1))

    grammar.register('nspaces', parsers.Repeat(parsers.Choice() \
                                               .either(parsers.Token('space')) \
                                               .orelse(parsers.Token('newline'))
                                               , minimum=1))

    grammar.register('type_var', parsers.Token('type_var'))
    grammar.register('identifier', parsers.Token('identifier'))

    # <type-expr> ::= <bool-type> | <int-type> | <float-type> | <Number-type>
    #               | <str-type> | <NoneType-type>
    #               | <type-var> | <identifier>

    bool_parser = parsers.Token('bool_type')
    def bool_xform_result(result):
        result.content = BoolType(annotation=result)
        return result

    bool_parser.xform_result = bool_xform_result
    grammar.register('bool_type', bool_parser)

    anything_parser = parsers.Token('Anything_type')
    def anything_xform_result(result):
        result.content = Anything(annotation=result)
        return result
    anything_parser.xform_result = anything_xform_result
    grammar.register('Anything_type', anything_parser)

    int_parser = parsers.Token('int_type')
    def int_xform_result(result):
        result.content = IntType(annotation=result)
        return result
    int_parser.xform_result = int_xform_result
    grammar.register('int_type', int_parser)

    float_parser = parsers.Token('float_type')
    def float_xform_result(result):
        result.content = FloatType(annotation=result)
        return result
    float_parser.xform_result = float_xform_result
    grammar.register('float_type', float_parser)

    Number_parser = parsers.Token('Number_type')
    def Number_xform_result(result):
        result.content = NumberType(annotation=result)
        return result
    Number_parser.xform_result = Number_xform_result
    grammar.register('Number_type', Number_parser)

    Image_parser = parsers.Token('Image_type')
    def Image_xform_result(result):
        result.content = ImageType(annotation=result)
        return result
    Image_parser.xform_result = Image_xform_result
    grammar.register('Image_type', Image_parser)

    str_parser = parsers.Token('str_type')
    def str_xform_result(result):
        result.content = StrType(annotation=result)
        return result
    str_parser.xform_result = str_xform_result
    grammar.register('str_type', str_parser)

    NoneType_parser = parsers.Token('NoneType_type')
    def NoneType_xform_result(result):
        result.content = NoneTypeType(annotation=result)
        return result
    NoneType_parser.xform_result = NoneType_xform_result
    grammar.register('NoneType_type', NoneType_parser)

    typevar_parser = parsers.Token('type_var')
    def typevar_xform_result(result):
        result.content = TypeVariable(result.content.value, annotation=result)
        return result
    typevar_parser.xform_result = typevar_xform_result
    grammar.register('type_var', typevar_parser)

    type_alias_parser = parsers.Token('identifier')
    def type_alias_xform_result(result):
        result.content = TypeAlias(result.content.value, annotation=result)
        return result
    type_alias_parser.xform_result = type_alias_xform_result
    grammar.register('type_alias', type_alias_parser)

    iterable_parser = parsers.Tuple() \
                      .skip(parsers.Token('Iterable_type')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('open_bracket')) \
                      .forget(grammar.ref('spaces')) \
                      .element(grammar.ref('typeexpr')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('close_bracket'))

    def iterable_xform_result(result):
        result.content = IterableType(result.content.content, annotation=result)
        return result
    iterable_parser.xform_result = iterable_xform_result
    grammar.register('Iterable_type', iterable_parser)

    sequence_parser = parsers.Tuple() \
                      .skip(parsers.Token('Sequence_type')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('open_bracket')) \
                      .forget(grammar.ref('spaces')) \
                      .element(grammar.ref('typeexpr')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('close_bracket'))

    def sequence_xform_result(result):
        result.content = SequenceType(result.content.content, annotation=result)
        return result
    sequence_parser.xform_result = sequence_xform_result
    grammar.register('Sequence_type', sequence_parser)

    list_parser = parsers.Tuple() \
                      .skip(parsers.Token('list_type')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('open_bracket')) \
                      .forget(grammar.ref('spaces')) \
                      .element(grammar.ref('typeexpr')) \
                      .forget(grammar.ref('spaces')) \
                      .skip(parsers.Token('close_bracket'))

    def list_xform_result(result):
        result.content = ListType(result.content.content, annotation=result)
        return result
    list_parser.xform_result = list_xform_result
    grammar.register('list_type', list_parser)

    tuple_parser = parsers.Tuple() \
                        .skip(parsers.Token('tuple_type')) \
                        .forget(grammar.ref('spaces')) \
                        .skip(parsers.Token('open_bracket')) \
                        .forget(grammar.ref('spaces')) \
                        .element(parsers.List(grammar.ref('typeexpr'), sep='comma')
                                 .forget(grammar.ref('spaces'))) \
                        .forget(grammar.ref('spaces')) \
                        .skip(parsers.Token('close_bracket'))
                                 
    def tuple_xform_result(result):
        elem_types = []
        for elem_result in result.content.content:
            elem_types.append(elem_result.content)
            
        result.content = TupleType(elem_types, annotation=result)
        return result
    
    tuple_parser.xform_result = tuple_xform_result
    grammar.register('tuple_type', tuple_parser)
    

    type_expr = parsers.Choice() \
                       .forget(grammar.ref('spaces')) \
                       .either(grammar.ref('bool_type')) \
                       .orelse(grammar.ref('int_type')) \
                       .orelse(grammar.ref('float_type')) \
                       .orelse(grammar.ref('Number_type')) \
                       .orelse(grammar.ref('Image_type')) \
                       .orelse(grammar.ref('str_type')) \
                       .orelse(grammar.ref('NoneType_type')) \
                       .orelse(grammar.ref('Anything_type')) \
                       .orelse(grammar.ref('Iterable_type')) \
                       .orelse(grammar.ref('Sequence_type')) \
                       .orelse(grammar.ref('list_type')) \
                       .orelse(grammar.ref('tuple_type')) \
                       .orelse(grammar.ref('type_var')) \
                       .orelse(grammar.ref('type_alias'))

    grammar.register('typeexpr', type_expr)

    grammar.entry = grammar.ref('typeexpr')

    return grammar

def build_functype_grammar(grammar):
    
    dom_elem_parser = parsers.Tuple() \
                      .element(grammar.ref('typeexpr')) \
                      .skip(grammar.ref('nspaces')) \
                      .element(parsers.Optional(parsers.Tuple() \
                                                .skip(grammar.ref('spaces')) \
                                                .element(parsers.Choice() \
                                                         .either(parsers.Token('pow')) \
                                                         .orelse(parsers.Token('expr'))) \
                                                .skip(grammar.ref('spaces')) \
                                                .element(parsers.Token('natural'))))

    def dom_elem_xform_result(result):

        type_result = result.content[0]
        repeat_result = result.content[1]

        if repeat_result.content is None:
            result.content = type_result.content
            return result
        else:

            nb_repeat = int(repeat_result.content[1].content.value)
            new_content = [type_result.content for _ in range(nb_repeat)]
            result.content = new_content
            return result
        
    dom_elem_parser.xform_result = dom_elem_xform_result
    
    grammar.register('dom_elem', dom_elem_parser)

    domain_parser = parsers.List(grammar.ref('dom_elem'), sep='mult') \
                           .forget(grammar.ref('spaces'))

    def domain_xform_result(result):
        if result.content is None:
            return result
        
        domain_types = []
        for elem in result.content:
            if isinstance(elem.content, TypeAST):
                domain_types.append(elem.content)
            else:
                domain_types.extend(elem.content)

        result.content = domain_types
        return result
                
    domain_parser.xform_result = domain_xform_result

    grammar.register('domain_type', domain_parser)

    range_parser = parsers.Tuple() \
                          .element(grammar.ref('typeexpr')) \
                          .skip(grammar.ref('nspaces')) \
                          .element(parsers.Optional(parsers.Tuple() \
                                                    .skip(parsers.Token('add')) \
                                                    .skip(grammar.ref('spaces')) \
                                                    .element(parsers.Token('NoneType_type'))))

    grammar.register('range_type', range_parser)

    functype_parser = parsers.Tuple() \
                      .skip(grammar.ref('nspaces')) \
                      .element(grammar.ref('domain_type')) \
                      .skip(grammar.ref('nspaces')) \
                      .skip(parsers.Token('arrow')) \
                      .skip(grammar.ref('spaces')) \
                      .element(grammar.ref('range_type'))

    def functype_parser_xform_result(result):
        #import pdb ; pdb.set_trace()
        param_types = []
        params_content = result.content[0]
        if params_content.content:
            for param_content in params_content.content:
                param_types.append(param_content)

        range_content = result.content[1].content
        #print("range content=",range_content)
        range_type = None
        range_type = range_content[0].content
        #print("range_type=",range_type)

        if range_content[1].content is None:
            partial_function = False
        else:
            partial_function = True

        result.content = FunctionType(param_types, range_type, partial_function, annotation=result)

        return result

    functype_parser.xform_result = functype_parser_xform_result

    grammar.entry = functype_parser

    return grammar

class TypeParser:
    def __init__(self):
        self.tokenizer = type_tokenizer()
        self.typeexpr_grammar = build_typeexpr_grammar()
        self.functype_grammar = build_functype_grammar(build_typeexpr_grammar())

    def parse_typeexpr_from_string(self, string):
        parser = LLParsing(self.typeexpr_grammar)
        parser.tokenizer = self.tokenizer
        self.tokenizer.from_string(string)
        return parser.parse()

    def parse_functype_from_string(self, string):
        parser = LLParsing(self.functype_grammar)
        parser.tokenizer = self.tokenizer
        self.tokenizer.from_string(string)
        return parser.parse()

def function_type_parser(string):
    parser = TypeParser()
    return parser.parse_functype_from_string(string)

def type_expression_parser(string):
    parser = TypeParser()
    return parser.parse_typeexpr_from_string(string)

TYPE_DEF_REGEXP = re.compile(r"\A#[ \t]+type[ \t]+([a-zA-Z][a-zA-Z_0-9]*)[ \t]*=[ \t]*(.*)$")

def type_def_parser(string):
    m = re.match(TYPE_DEF_REGEXP, string)
    if m is None:
        return (None, None)

    type_name = m.group(1)

    type_def = type_expression_parser(m.group(2))
    return (type_name, type_def)

if __name__ == "__main__":
    type_parser = TypeParser()

    # atomic types
    result1 = type_parser.parse_typeexpr_from_string("bool")
    print(repr(result1.content))

    result2 = type_parser.parse_typeexpr_from_string("  int  ")
    print(repr(result2.content))

    result3 = type_parser.parse_typeexpr_from_string("float")
    print(repr(result3.content))

    result4 = type_parser.parse_typeexpr_from_string("Number")
    print(repr(result4.content))

    result5 = type_parser.parse_typeexpr_from_string("str")
    print(repr(result5.content))

    result6 = type_parser.parse_typeexpr_from_string("NoneType")
    print(repr(result6.content))

    result7 = type_parser.parse_typeexpr_from_string("α")
    print(repr(result7.content))

    result8 = type_parser.parse_typeexpr_from_string("beta")
    print(repr(result8.content))

    result9 = type_parser.parse_typeexpr_from_string("Gamma")
    print(repr(result9.content))

    result10 = type_parser.parse_typeexpr_from_string("DELTA")
    print(repr(result10.content))

    result11 = type_parser.parse_typeexpr_from_string("GammA")
    print(repr(result11.content))

    # function types
    fresult1 = type_parser.parse_functype_from_string("int * float -> bool")
    print(repr(fresult1.content))

    fresult2 = type_parser.parse_functype_from_string("Number**3 -> Number")

    

