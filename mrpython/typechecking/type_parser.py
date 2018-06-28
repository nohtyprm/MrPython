
'''The parser for types'''

from ...popparser import (Grammar, tokens, parsers, expr, ParseResult)
from ..popparser.llparser import LLParsing
from ..popparser.tokenizer import Tokenizer


def type_tokenizer():
    tokenizer = Tokenizer()

    # punctuation
    tokenizer.add_rule('comma', tokens.Char(','))

    # spaces
    tokenizer.add_rule('space', tokens.CharSet(' ', '\t', '\r'))

    # symbols
    tokenizer.add_rule('arrow', tokens.Literal("->"))
    tokenizer.add_rule('expr', tokens.Literal("**"))
    tokenizer.add_rule('mult', tokens.Char('*'))

    # basic types
    tokenizer.add_rule('bool_type',tokens.Literal('bool'))
    tokenizer.add_rule('int_type', tokens.Literal('int'))
    tokenizer.add_rule('float_type', tokens.Literal('float'))
    tokenizer.add_rule('Number_type', tokens.Literal('Number'))
    tokenizer.add_rule('NoneType_type', tokens.Literal('NoneType'))
    tokenizer.add_rule('str_type', tokens.Literal('str'))

    # type variables
    tokenizer.add_rule('type_var'
                       , tokens.LiteralSet( "α", "alpha", "Alpha", "ALPHA"
                                            , "β", "beta", "Beta", "BETA"
                                            , "γ", "gamma", "Gamma", "GAMMA"
                                            , "δ", "delta", "Delta", "DELTA"
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

    grammar.register('bool_type', parsers.Token('bool_type'))
    grammar.register('int_type', parsers.Token('int_type'))
    grammar.register('float_type', parsers.Token('float_type'))
    grammar.register('Number_type', parsers.Token('Number_type'))
    grammar.register('str_type', parsers.Token('str_type'))
    grammar.register('NoneType_type', parsers.Token('NoneType_type'))

    grammar.register('type_var', parsers.Token('type_var'))
    grammar.register('identifier', parsers.Token('identifier'))

    type_expr = parsers.ChoiceParser() \
                       .forget(grammar.ref('spaces')) \
                       .either(grammar.ref('bool_type')) \
                       .orElse(grammar.ref('int_type')) \
                       .orElse(grammar.ref('float_type')) \
                       .orElse(grammar.ref('Number type')) \
                       .orElse(grammar.ref('str_type')) \
                       .orElse(grammar.ref('NoneType_type')) \
                       .orElse(grammar.ref('type_var')) \
                       .orElse(grammar.ref('identifier'))

    grammar.register('typeexpr', type_expr)

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
    grammar.register('func_type', functype_parsre)

    return grammar

class TypeParser:
    def __init__(self):
        self.tokenizer = type_tokenizer()
        self.typeexpr_grammar = build_typeexpr_grammar()
        self.functype_grammar = build_functype_grammar(build_typeexpr_grammar())

    def parse_typeexpr_from_string(self, string):
        parser = LLParsing(self.typeexpr_grammar)
        parser.tokenizer = self.tokenizer
        tokenizer.from_string(string)
        return parser.parse()

    def parse_functype_from_string(self, string):
        parser = LLParsing(self.functype_grammar)
        parser.tokenizer = self.tokenizer
        tokenizer.from_string(string)
        return parser.parse()


if __name__ == "__main__":
    type_parser = TypeParser()

    # atomic types
    result1 = type_parser.parse_typeexpr_from_string("bool")
    print(result1)
 
