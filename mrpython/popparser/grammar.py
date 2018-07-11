'''Representation of parsing grammars.

Created on 24 août 2012

@author: F. Peschanski
'''

from popparser import ParseException, Parser


class Grammar:
    def __init__(self):
        self.__rules = {}  # dict[str,parser]

    def register(self, rule_name, parser):
        assert isinstance(parser, Parser)
        self.__rules[rule_name] = parser

    def fetch(self, rule_name):
        if rule_name not in self.__rules:
            return None
        return self.__rules[rule_name]

    def ref(self, rule_name):
        return RefParser(self, rule_name)

    @property
    def entry(self):
        return self.fetch("init")

    @entry.setter
    def entry(self, parser):
        self.__rules['init'] = parser

    def __str(self):
        msg = 'Grammar:\n'
        for name, parser in self.__rules.items():
            msg += name + ' ::= ' + str(parser) + '\n'
        return msg


class RefParser(Parser):
    def __init__(self, grammar, rule_name):
        Parser.__init__(self)
        self.grammar = grammar
        self.rule_name = rule_name

    @property
    def token_type(self):
        parser = self.grammar.fetch(self.rule_name)
        if parser is None:
            return None
        else:
            return parser.token_type

    def do_parse(self, llparser):
        parser = self.grammar.fetch(self.rule_name)
        if parser is None:
            raise ParseException("No such rule in grammar: " + self.rule_name)
        return parser.parse(llparser)

    def __str__(self):
        return "<{0}>".format(self.rule_name)
