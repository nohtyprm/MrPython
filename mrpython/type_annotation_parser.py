from popparser import Grammar, parsers, tokens
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer

class TypeAnnotation:
    def __init__(self, name, kind):
        self.name = name
        self.type = kind

class TypeAnnotationParser:
    def __init__(self):
      self.grammar = Grammar()
      self.forge_grammar(self.grammar)

    def forge_tokenizer(self, tokenizer):

        # punctuation
        tokenizer.add_rule(tokens.Char('octothorpe', '#'))
        tokenizer.add_rule(tokens.Char('colon', ':'))

        # spaces
        tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r'))

        # identifiers
        tokenizer.add_rule(tokens.Regexp('identifier',
                                             "[a-zA-Z_][a-zA-Z_0-9]*'*"))
        return tokenizer

    def forge_grammar(self, grammar):

        spaces_parser = parsers.Repeat(parsers.Token('space'), minimum=1)
        grammar.register('spaces', spaces_parser)

        grammar.register('colon', parsers.Token('colon'))
        grammar.register('octothorpe', parsers.Token('octothorpe'))
        grammar.register('identifier', parsers.Token('identifier'))
        parser = parsers.Tuple().skip(grammar.ref('spaces'))\
                                .skip(grammar.ref('octothorpe'))\
                                .skip(grammar.ref('spaces'))\
                                .element(grammar.ref('identifier'))\
                                .skip(grammar.ref('spaces'))\
                                .skip(grammar.ref('colon'))\
                                .skip(grammar.ref('spaces'))\
                                .element(grammar.ref('identifier'))

        # Get a minimally structured result
        def type_annot_xform(result):
            name = result.content[0]
            kind = result.content[1]
            return TypeAnnotation(name.content.value, kind.content.value)

        parser.xform_content = type_annot_xform

        grammar.register('type_annot', parser)

        grammar.entry = grammar.ref('type_annot')

    def parse_from_string(self, string):
        tokenizer = Tokenizer()
        self.forge_tokenizer(tokenizer)
        parser = LLParsing(self.grammar)
        parser.tokenizer = tokenizer
        tokenizer.from_string(string)
        return parser.parse()
