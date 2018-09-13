'''Tokens and tokenization

Created on 24 august 2012

@author: F. Peschanski
'''

from copy import deepcopy
from collections import defaultdict

from popparser.llparser import ParsePosition


class Token:
    def __init__(self, token_type, value, start_pos, end_pos):
        self.token_type = token_type
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos

    @property
    def iseof(self):
        return False

    @property
    def iserror(self):
        return False

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Token(token_type='{0}', value='{1}', "\
               "start_pos={2}, end_pos={3})"\
               .format(self.token_type, self.value,
                       self.start_pos, self.end_pos)


class EOFToken(Token):
    def __init__(self, pos):
        Token.__init__(self, '<<EOF>>', '<<EOF>>', pos, pos)

    @property
    def iseof(self):
        return True

    @property
    def pos(self):
        return self.start_pos

    def __str__(self):
        return '<<EOF>>'

    def __repr__(self):
        return "EOFToken(start_pos={0}, end_pos={1})"\
               .format(self.start_pos, self.end_pos)


class ErrorToken(Token):
    def __init__(self, message, pos):
        Token.__init__(self, '<<ERROR>>', message, pos, pos)

    @property
    def message(self):
        return str(self.value)

    @property
    def iserror(self):
        return True

    def __str__(self):
        return "Token error: " + self.message

    def __repr__(self):
        return "ErrorToken(token_type='{0}', msg='{1}', "\
               "start_pos={2}, end_pos={3})"\
               .format(self.token_type, self.value,
                       self.start_pos, self.end_pos)


class Tokenizer:
    def __init__(self):
        self.__token_rules = {}  # dict[str,List[TokenRule]]
        self.__none_rules = []  # rules with no lookup available
        self.__backend = None

        self.reset()

    def reset(self):
        self.pos = ParsePosition()
        self.lines = defaultdict()  # dict[int,ParsePosition]

    @property
    def backend(self):
        return self.__backend

    @backend.setter
    def backend(self, backend_):
        self.backend = backend_

    def from_string(self, string):
        self.__backend = StrTokenizer(self, string)
        self.reset()

    @property
    def position(self):
        return self.pos

    def add_rule(self, token_rule):
        if token_rule.lookups is None:
            self.__none_rules.append(token_rule)
        else:
            for lookup in token_rule.lookups:
                if lookup not in self.__token_rules:
                    rules = []
                    self.__token_rules[lookup] = rules
                else:
                    rules = self.__token_rules[lookup]
                rules.append(token_rule)

    def forward(self):
        char = self.peek_char()
        if char is None:
            return False  # cannot advance forward
        if char == '\n':
            self.lines[self.pos.offset] = self.pos
            self.pos = self.pos.next_line()
        else:
            self.pos = self.pos.next_char()
        return True

    def forwards(self, nb):
        if nb < 0:
            return self.backwards(-nb)
        saved_pos = self.pos
        saved_lines = deepcopy(self.lines)
        for _ in range(nb):
            moved = self.forward()
            if not moved:
                self.pos = saved_pos
                self.lines = saved_lines
                return False
        # end of for
        return True

    def backward(self):
        if self.pos.offset == 0:
            return False
        try:
            prev = self.lines[self.pos.offset - 1]
            self.pos = prev
            del self.lines[self.pos.offset]
            return True
        except KeyError:
            # not an end of line
            self.pos = self.pos.prev_char()
            return True

    def backwards(self, nb):
        if nb < 0:
            return self.forwards(-nb)
        saved_pos = self.pos
        saved_lines = deepcopy(self.lines)
        for _ in range(nb):
            moved = self.backward()
            if not moved:
                self.pos = saved_pos
                self.lines = saved_lines
                return False
        # end of for
        return True

    def peek_char(self):
        if not self.__backend:
            raise NotImplementedError("No backend")
        else:
            return self.__backend.peek_char()

    def peek_line(self):
        if not self.__backend:
            raise NotImplementedError("No backend")
        else:
            return self.__backend.peek_line()

    @property
    def at_eof(self):
        return self.peek_char() is None

    def next_char(self):
        char = self.peek_char()
        if char is None:
            return None
        self.forward()
        return char

    def consume(self, string):
        saved_pos = self.pos
        saved_lines = deepcopy(self.lines)
        for char in string:
            next_char = self.peek_char()
            if (next_char is None) or (next_char != char):
                self.pos = saved_pos
                self.lines = saved_lines
                return False
            # ok, same char
            self.forward()
        # end of for, the string has been consumed
        return True

    def put_back(self, token):
        self.backwards(token.end_pos.offset - token.start_pos.offset)
        #XXX: check needed ?
        #if self.peek() != token:
        #    raise ValueError("Wrong token to put back")

    def next(self):
        '''Return the next token.
        '''
        lookup = self.peek_char()
        if lookup is None:
            return EOFToken(self.pos)
        if lookup in self.__token_rules:
            rules = self.__token_rules[lookup] + self.__none_rules
        else:
            rules = self.__none_rules

        for rule in rules:
            token = rule.recognize(self)
            if token is not None:
                return token

        return ErrorToken(repr(lookup), self.pos)

    def peek(self):
        saved_pos = self.pos
        saved_lines = deepcopy(self.lines)
        token = self.next()
        self.pos = saved_pos
        self.lines = saved_lines
        return token

    def substring(self, start_offset, end_offset):
        return self.__backend.substring(start_offset, end_offset)

    def __str__(self):
        msg = ""
        msg += str(self.pos.line_pos)
        msg += ": "
        if self.pos.line_pos in self.lines:
            start_offset = self.lines[self.pos.line_pos]
        else:
            start_offset = 0

        end_offset = self.pos.offset
        msg += self.substring(start_offset, end_offset)
        msg += "_"
        msg += self.peek_line()
        return msg

    def __repr__(self):
        return "<Tokenizer: " + str(self) + ">"


class TokenizerBackend:
    pass


class StrTokenizer(TokenizerBackend):
    def __init__(self, tokenizer, string):
        self.tokenizer = tokenizer
        self.string = string

    def peek_char(self):
        if self.tokenizer.pos.offset > len(self.string) - 1:
            return None
        return self.string[self.tokenizer.pos.offset]

    def peek_line(self):
        line = None
        offset = self.tokenizer.pos.offset
        lenstr = len(self.string)
        while True:
            if offset >= lenstr:
                break
            if line is None:
                line = ""
            char = self.string[offset]
            if char == '\n':
                break
            line += char
            offset += 1
        # at the end of the line
        return line

    def substring(self, start_offset, end_offset):
        return self.string[start_offset:end_offset]
