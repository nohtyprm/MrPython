'''Token rules.

Created on 24 august 2012

@author: F. Peschanski
'''

from popparser.tokenizer import Token

import re


class TokenRule:
    def __init__(self, token_type):
        self.token_type = token_type

    @property
    def lookups(self):
        raise NotImplementedError("Abstract method")

    def recognize(self, tokenizer):
        raise NotImplementedError("Abstract method")


class CharPredicate(TokenRule):
    def __init__(self, token_type):
        TokenRule.__init__(self, token_type)

    def predicate(self, char):
        raise NotImplementedError("Abstract methods")

    def recognize(self, tokenizer):
        start_pos = tokenizer.position
        next_ = tokenizer.peek_char()
        if (next_ is None) or (not self.predicate(next_)):
            return None
        tokenizer.forward()
        return Token(self.token_type, next_, start_pos, tokenizer.position)


class Char(CharPredicate):
    def __init__(self, token_type, char):
        CharPredicate.__init__(self, token_type)
        self.char = char

    @property
    def lookups(self):
        return {self.char}

    def predicate(self, char):
        return char == self.char


class CharSet(CharPredicate):
    def __init__(self, token_type, *charset):
        CharPredicate.__init__(self, token_type)
        self.charset = charset

    @property
    def lookups(self):
        return self.charset

    def predicate(self, char):
        return char in self.charset


class CharInterval(CharPredicate):
    def __init__(self, token_type, min_char, max_char):
        assert min_char <= max_char
        CharPredicate.__init__(self, token_type)
        self.min_char = min_char
        self.max_char = max_char

    @property
    def lookups(self):
        return {chr(code) for code\
                          in range(ord(self.min_char),
                                   ord(self.max_char) + 1)}

    def predicate(self, char):
        return ord(self.min_char) <= ord(char) <= ord(self.max_char)


class Literal(TokenRule):
    def __init__(self, token_type, literal):
        assert isinstance(literal, str)
        assert len(literal) > 0
        TokenRule.__init__(self, token_type)
        self.literal = literal

    @property
    def lookups(self):
        return {self.literal[0]}

    def recognize(self, tokenizer):
        start_pos = tokenizer.position
        if tokenizer.consume(self.literal):
            return Token(self.token_type, self.literal,
                         start_pos, tokenizer.position)
        else:
            return None


class LiteralSet(TokenRule):
    def __init__(self, token_type, *literals):
        TokenRule.__init__(self, token_type)
        self.literals = literals
        self.__lookups = None

    @property
    def lookups(self):
        if not self.__lookups:
            self.__lookups = set()
            for literal in self.literals:
                self.__lookups.add(literal[0])
        return self.__lookups

    def recognize(self, tokenizer):
        start_pos = tokenizer.position
        for literal in self.literals:
            if tokenizer.consume(literal):
                return Token(self.token_type, literal,
                             start_pos, tokenizer.position)
        # end of for, no matching literal found
        return None


class RegexpRule(TokenRule):
    def __init__(self, token_type, regexp, lookups=None):
        TokenRule.__init__(self, token_type)
        self.regexp = re.compile(regexp)
        self.__lookups = lookups

    def build_token(self, match_obj, parsed_str, start_pos, end_pos):
        raise NotImplementedError("Abstract method")

    @property
    def lookups(self):
        return self.__lookups

    def recognize(self, tokenizer):
        start_pos = tokenizer.position
        line = tokenizer.peek_line()
        if line is None:
            return None
        match_obj = self.regexp.match(line)
        if match_obj is None:
            return None
        parsed_str = match_obj.group(0)  # entire match
        ok = tokenizer.consume(parsed_str)
        assert ok  # in case ...
        return self.build_token(match_obj, parsed_str,
                                start_pos, tokenizer.position)


class Regexp(RegexpRule):
    def __init__(self, token_type, regexp, lookups=None):
        RegexpRule.__init__(self, token_type, regexp, lookups)

    def build_token(self, _, parsed_str, start_pos, end_pos):
        return Token(self.token_type, parsed_str,
                     start_pos, end_pos)
