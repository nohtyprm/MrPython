'''Basic parsers

Created on 7 august 2012

@author: fredo
'''

from collections import defaultdict

from popparser.llparser import ParseResult, ParseError


#==============================================================================
# ABSTRACT BASE CLASS FOR PARSERS
#==============================================================================

class Parser:
    '''The root abstract class for parsers.

    Remark: it is possible to apply transformations to
    parse results or result contents, e.g. transforming
    a token content by a simple string,  a string by
    a numeral, etc.
    The two method available are:
      1) xform_result: ParseResult -> ParseResult
      2) xform_content: ParseResult -> Content

    Transforming result has priority over transforming content
    '''
    def __init__(self):
        self.xform_result = None
        self.xform_content = None
        self.forget_parsers = {}

    def forget(self, parser):
        self.forget_parsers[parser.token_type] = parser
        return self

    def forget_parse(self, llparsing):
        while True:
            next_token = llparsing.peek_token()
            if next_token.token_type in self.forget_parsers:
                forget_parser = self.forget_parsers[next_token.token_type]
                result = forget_parser.parse(llparsing)
                if result.iserror:
                    return result # ?
            else:
                return None

    @property
    def token_type(self):
        raise NotImplementedError("Abstract method")

    def parse(self, llparsing):
        if llparsing.debug_mode:
            llparsing.debug.enter(llparsing, self)

        result = self.forget_parse(llparsing)
        if result is not None and result.iserror:
            return result

        result = self.do_parse(llparsing)

        fresult = self.forget_parse(llparsing)
        if fresult is not None and fresult.iserror:
            return fresult

        if llparsing.debug_mode:
            llparsing.debug.leave(llparsing, self)

        if not result.iserror:
            if self.xform_result:
                result = self.xform_result(result)
            elif self.xform_content:
                result = ParseResult(self.xform_content(result),
                                     result.start_pos, result.end_pos)
        return result

    def do_parse(self, llparsing):
        raise NotImplementedError("Abstract method")


#==============================================================================
# TOKEN PARSING
#==============================================================================


class Token(Parser):
    '''Parse a single token.
    '''
    def __init__(self, token_type):
        Parser.__init__(self)
        self.__token_type = token_type

    @property
    def token_type(self):
        return self.__token_type

    def do_parse(self, llparsing):
        start_pos = llparsing.position
        token = llparsing.peek_token()
        if token.token_type == self.__token_type:
            return ParseResult(llparsing.next_token(),
                               start_pos, llparsing.position)
        else:
            return ParseError("Expecting '{0}' token"\
                              .format(self.__token_type),
                              start_pos, llparsing.position)


class EOF(Token):
    '''Parse End of file (EOF).
    '''
    def __init__(self):
        Token.__init__(self, '<<EOF>>')


#==============================================================================
# TUPLE PARSER
#==============================================================================

class Tuple(Parser):
    '''Tuple parser.
    '''
    def __init__(self):
        Parser.__init__(self)
        self.__parsers = []
        self.__skips = defaultdict()

    def element(self, parser):
        self.__parsers.append(parser)
        return self  # chaining API

    def skip(self, parser):
        if len(self.__parsers) not in self.__skips:
            self.__skips[len(self.__parsers)] = []
        skips = self.__skips[len(self.__parsers)]
        skips.append(parser)
        return self

    @property
    def token_type(self):
        if 0 in self.__skips:
            first = self.__skips[0]
            if first:
                return first[0].token_type
        elif self.__parsers:
            return self.__parsers[0].token_type
        else:
            return None

    def do_parse(self, llparser):
        start_pos = llparser.position
        results = []
        for i in range(len(self.__parsers)):
            # forget parsers
            result = self.forget_parse(llparser)
            if result is not None and result.iserror:
                return result

            # skip parsers
            skips = None
            if i in self.__skips:
                skips = self.__skips[i]
            if skips:
                for skip in skips:
                    result = skip.parse(llparser)
                    if result.iserror:
                        return result
            # element
            parser = self.__parsers[i]
            result = parser.parse(llparser)
            if result.iserror:
                return result
            results.append(result)

        # last skips
        skips = None
        if len(self.__parsers) in self.__skips:
            skips = self.__skips[len(self.__parsers)]
        if skips:
            for skip in skips:
                result = skip.parse(llparser)
                if result.iserror:
                    return result

        end_pos = llparser.position
        if len(results) == 1:
            results = results[0]
        return ParseResult(results, start_pos, end_pos)


#==============================================================================
# REPEAT PARSER
#==============================================================================

class Repeat(Parser):
    '''Repeat parser.
    '''
    def __init__(self, parser, minimum=0):
        Parser.__init__(self)
        self.minimum = minimum
        self.parser = parser

    @property
    def token_type(self):
        return self.parser.token_type

    def do_parse(self, llparser):
        start_pos = llparser.position
        count = 0
        results = []
        while True:
            # forget parsers
            result = self.forget_parse(llparser)
            if result is not None and result.iserror:
                return result

            result = self.parser.parse(llparser)
            if result.iserror:
                if count == 0 and self.minimum == 0:
                    return ParseResult(None, start_pos, llparser.position)
                elif 0 < count < self.minimum:
                    return ParseError('{0} repetition(s) is not enough '
                                      '(minimum={1})'\
                                      .format(count, self.minimum),\
                                      start_pos,\
                                      llparser.position)
                    # TODO: stacking errors ?
                else:
                    return ParseResult(results, start_pos, llparser.position)
            results.append(result)


#==============================================================================
# LIST PARSER
#==============================================================================

class List(Parser):
    '''List parser.
    '''
    def __init__(self, of, open=None, close=None, sep=None, minimum=0):
        Parser.__init__(self)
        self.minimum = minimum
        self.open_token = open
        self.close_token = close
        self.sep_token = sep
        self.parser = of

    @property
    def token_type(self):
        if self.open_token is None:
            return self.parser.token_type
        else:
            return self.open_token

    def do_parse(self, llparser):
        start_pos = llparser.position
        count = 0
        results = []
        if self.open_token is not None:
            next_token = llparser.peek_token()
            if next_token.token_type != self.open_token:
                return ParseError("Expecting open list token '{0}' got: {1}"\
                        .format(self.open_token, next_token.token_type),
                        next_token.start_pos,
                        next_token.end_pos)
            llparser.next_token()
        while True:
            # forget parsers
            result = self.forget_parse(llparser)
            if result is not None and result.iserror:
                return result

            result = self.parser.parse(llparser)
            if result.iserror:
                break
            # result is not an error
            results.append(result)
            count += 1

            # forget parsers
            result = self.forget_parse(llparser)
            if result is not None and result.iserror:
                return result

            # separator
            if self.sep_token is not None:
                next_token = llparser.peek_token()
                if next_token.token_type != self.sep_token:
                    break
                llparser.next_token()
        # end of loop
        if self.close_token is not None: 
            next_token = llparser.peek_token()
            if next_token.token_type != self.close_token:
                return ParseError("Expecting close list token "
                                              "'{0}' got: {1}"\
                        .format(self.close_token, next_token.token_type),
                        next_token.start_pos,
                        next_token.end_pos)

            llparser.next_token()

        if count == 0 and self.minimum == 0:
            return ParseResult(None, start_pos, llparser.position)
        elif 0 < count < self.minimum:
            return ParseError('{0} element(s) is not enough '
                                  '(minimum={1})'\
                                  .format(count, self.minimum),\
                                  start_pos,\
                                  llparser.position)

        return ParseResult(results, start_pos, llparser.position)

#==============================================================================
# OPTIONAL PARSER
#==============================================================================

class Optional(Parser):
    '''Optional parser.
    '''
    def __init__(self, parser):
        Parser.__init__(self)
        self.parser = parser

    @property
    def token_type(self):
        return self.parser.token_type

    def do_parse(self, llparser):
        start_pos = llparser.position
        result = self.parser.parse(llparser)
        if result.iserror:
            return ParseResult(None, start_pos, llparser.position)
        # ok, parsed
        return result


#==============================================================================
# CHOICE PARSER
#==============================================================================

class Choice(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.__branches = []
        self.__dispatch = None
        self.__static_token_types = set()

    class StateError(Exception):
        pass

    def either(self, parser):
        if self.__branches:
            raise Choice.StateError("Branch 'either' on as first choice")
        return self.orelse(parser)

    def orelse(self, parser):
        if not isinstance(parser.token_type, str):
            raise Choice.StateError("Token type must be a string, provided:" + repr(parser.token_type))
        if parser.token_type in self.__static_token_types:
            raise Choice.StateError("Token type '" + parser.token_type \
                                    + "' ambiguous")
        self.__static_token_types.add(parser.token_type)
        self.__branches.append(parser)
        return self

    def _build_dispatch(self):
        self.__dispatch = {}
        for branch in self.__branches:
            token_type = branch.token_type
            if not isinstance(token_type, str):
                raise Choice.StateError("Token type must be a string, provided:" + repr(token_type) + "\nParser is: "
                                        + str(branch))
            if token_type in self.__dispatch:
                raise Choice.StateError("Token type '" + token_type \
                                        + "' ambigous")
            self.__dispatch[token_type] = branch

    def explain_token_types(self):
        msg = ""
        count = 0
        for token_type in self.__dispatch:
            msg += "'" + str(token_type) + "'"
            if count < len(self.__dispatch) - 1:
                msg += ", or "
            count += 1

        return msg

    def do_parse(self, llparser):
        if not self.__dispatch:
            self._build_dispatch()

        token = llparser.peek_token()

        if token.token_type not in self.__dispatch:
            return ParseError("Unexpected token type '"\
                              + str(token.token_type) + "' expecting: "\
                              + self.explain_token_types(), token.start_pos, token.end_pos)
        branch = self.__dispatch[token.token_type]

        result = branch.parse(llparser)
        return result

    def __str__(self):
        msg = ""
        count = 0
        for branch in self.__branches:
            msg += str(branch)
            if count < len(self.__branches) - 1:
                msg += " | "
            count += 1
        return msg
