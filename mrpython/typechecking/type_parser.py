
'''The parser for types'''

import os.path, sys

pop_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "popparser", "src")
#print("pop path=", pop_path)
sys.path.append(pop_path)


from popparser import (Grammar, tokens, parsers, expr, ParseResult)
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer

from type_ast import *

def type_tokenizer():
    tokenizer = Tokenizer()

    # punctuation
    tokenizer.add_rule(tokens.Char('comma', ','))

    # spaces
    tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r'))

    # symbols
    tokenizer.add_rule(tokens.Literal('arrow', "->"))
    tokenizer.add_rule(tokens.Literal('expr', "**"))
    tokenizer.add_rule(tokens.Char('mult', '*'))

    # basic types
    tokenizer.add_rule(tokens.Literal('bool_type', 'bool'))
    tokenizer.add_rule(tokens.Literal('int_type', 'int'))
    tokenizer.add_rule(tokens.Literal('float_type', 'float'))
    tokenizer.add_rule(tokens.Literal('Number_type', 'Number'))
    tokenizer.add_rule(tokens.Literal('NoneType_type', 'NoneType'))
    tokenizer.add_rule(tokens.Literal('str_type', 'str'))

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

    # identifiers
    tokenizer.add_rule(tokens.Regexp('identifier',
                                     "[a-zA-Z_][a-zA-Z_0-9]*'*"))
    return tokenizer

def build_typeexpr_grammar(grammar=None):
    if grammar is None:
        grammar = Grammar()

    grammar.register('spaces', parsers.Repeat(parsers.Token('space'), minimum=1))
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

    str_parser = parsers.Token('str_type')
    def str_xform_result(result):
        result.content = StrType(annotation=result)
        return result
    str_parser.xform_result = str_xform_result
    grammar.register('str_type', str_parser)

    NoneType_parser = parsers.Token('NoneType_type')
    def NoneType_xform_result(result):
        result.content = NoneType(annotation=result)
        return result
    NoneType_parser.xform_result = NoneType_xform_result
    grammar.register('NoneType_type', NoneType_parser)

    typevar_parser = parsers.Token('type_var')
    def typevar_xform_result(result):
        result.content = TypeVariable(result.content.value, annotation=result)
        return result
    typevar_parser.xform_result = typevar_xform_result
    grammar.register('type_var', typevar_parser)

    grammar.register('identifier', parsers.Token('identifier'))

    type_expr = parsers.Choice() \
                       .forget(grammar.ref('spaces')) \
                       .either(grammar.ref('bool_type')) \
                       .orelse(grammar.ref('int_type')) \
                       .orelse(grammar.ref('float_type')) \
                       .orelse(grammar.ref('Number_type')) \
                       .orelse(grammar.ref('str_type')) \
                       .orelse(grammar.ref('NoneType_type')) \
                       .orelse(grammar.ref('type_var')) \
                       .orelse(grammar.ref('identifier'))

    grammar.register('typeexpr', type_expr)

    grammar.entry = grammar.ref('typeexpr')

    return grammar

def build_functype_grammar(grammar):
    domain_parser = parsers.List(grammar.ref('type_expr'), sep='mult') \
                           .forget(grammar.ref('spaces'))
    grammar.register('domain_type', domain_parser)

    functype_parser = parsers.Tuple() \
                      .element(grammar.ref('domain_type')) \
                      .skip(grammar.ref('spaces')) \
                      .skip(parsers.Token('arrow')) \
                      .skip(grammar.ref('spaces')) \
                      .element(grammar.ref('range_type'))
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
