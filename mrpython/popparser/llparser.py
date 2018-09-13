'''LL(1) parsing framework

Created on 7 august 2012

@author: F. Peschanski
'''

from popparser.debug import ParseDebug


class LLParsing:
    def __init__(self, grammar, debug_mode=False):
        self.__grammar = grammar
        self.__debug_mode = debug_mode
        self.__debug = None
        self.__tokenizer = None

    @property
    def debug_mode(self):
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, ndebug_mode):
        self.__debug_mode = ndebug_mode

    @property
    def debug(self):
        return self.__debug

    @property
    def tokenizer(self):
        return self.__tokenizer

    @tokenizer.setter
    def tokenizer(self, ntokenizer):
        self.__tokenizer = ntokenizer

    @property
    def grammar(self):
        return self.__grammar

    @property
    def position(self):
        return self.__tokenizer.position

    def peek_token(self):
        assert(self.__tokenizer)
        token = self.__tokenizer.peek()
        if self.__debug_mode:
            self.__debug.peek_token(self, token)
        return token

    def next_token(self):
        assert(self.__tokenizer)
        token = self.__tokenizer.next()
        if self.__debug_mode:
            self.__debug.next_token(self, token)
        return token

    def put_back_token(self, token):
        self.__tokenizer.put_back(token)

    def parse(self):
        if not self.__tokenizer:
            raise AttributeError("Missing tokenizer")
        if not self.__grammar:
            raise AttributeError("Missing grammar")

        start_parser = self.__grammar.entry
        if not start_parser:
            raise AttributeError("No start parser in grammar")

        self.__debug = ParseDebug()

        result = start_parser.parse(self)

        return result

    def __repr__(self):
        return "<LLParsing:" + str(self.__tokenizer)


class ParseResult:
    def __init__(self, content, start_pos, end_pos):
        self.content = content
        self.start_pos = start_pos
        self.end_pos = end_pos

    @property
    def iserror(self):
        return False

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        return "ParseResult(content={0}, start_pos={1}, end_pos={2}"\
            .format(repr(self.content),
                    repr(self.start_pos),
                    repr(self.end_pos))


class ParseError(ParseResult):
    def __init__(self, msg, start_pos, end_pos):
        ParseResult.__init__(self, msg, start_pos, end_pos)

    @property
    def iserror(self):
        return True

    def __str__(self):
        return "Error at {0}: {1}".format(str(self.end_pos), str(self.content))

    def __repr(self):
        return "ParseError(msg={0}, start_pos={1}, end_pos={2}"\
            .format(repr(self.content),
                    repr(self.start_pos),
                    repr(self.end_pos))


class ParsePosition:
    def __init__(self, offset=0, line_pos=1, char_pos=1):
        self.offset = offset
        self.line_pos = line_pos
        self.char_pos = char_pos

    def next_line(self):
        return ParsePosition(self.offset + 1, self.line_pos + 1, 1)

    def next_char(self):
        return ParsePosition(self.offset + 1, self.line_pos, self.char_pos + 1)

    def prev_char(self):
        return ParsePosition(self.offset - 1, self.line_pos, self.char_pos - 1)

    def first_char(self):
        return ParsePosition(self.offset - self.char_pos + 1,
                             self.line_pos,
                             1)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other is self:
            return True

        return other.offset == self.offset\
           and other.line_pos == self.line_pos\
           and other.char_pos == self.char_pos

    def __lt__(self, other):
        assert isinstance(other, self.__class__)
        return self.offset < other.offset

    def __le__(self, other):
        assert isinstance(other, self.__class__)
        return self.offset <= other.offset

    def __gt__(self, other):
        assert isinstance(other, self.__class__)
        return self.offset > other.offset

    def __ge__(self, other):
        assert isinstance(other, self.__class__)
        return self.offset >= other.offset

    def __str__(self):
        return 'line={0}, char={1}'.format(self.line_pos,
                                           self.char_pos)

    def __repr__(self):
        return 'ParsePosition(offset={0}, line_pos={1}, char_pos={2})'\
            .format(self.offset, self.line_pos, self.char_pos)
