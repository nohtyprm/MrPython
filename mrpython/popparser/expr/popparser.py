'''Top-down precedence-operated parser algorithm.

Created on 25 august 2012

@author: F. Peschanski
'''

from popparser import Parser, ParseError


class ExprParser(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.expressions = {}
        self.token = None
        self.llparser = None
        self.skip_tokens = set()

    @property
    def token_type(self):
        return None

    def register(self, token_type, expression):
        self.expressions[token_type] = expression
        return self

    def unregister(self, expr_type):
        del_tok_type = None
        for tok_type, expression in self.expressions.items():
            if expression.expr_type == expr_type:
                del_tok_type = tok_type
                break

        if del_tok_type:
            del self.expressions[del_tok_type]

    def skip_token(self, token_type):
        self.skip_tokens.add(token_type)
        return self

    def _tokens_skip(self, llparser):
        if not self.skip_tokens:
            return
        while True:
            next_token = llparser.peek_token()
            if next_token.token_type in self.skip_tokens:
                llparser.next_token()
            else:
                return

    def consume_token(self, token_type):
        if self.token.token_type != token_type:
            return ParseError("Expecting '" + token_type + "' but got '"\
                              + self.token.token_type + "'",\
                              self.token.start_pos, self.token.end_pos)
        self._tokens_skip(self.llparser)
        self.token = self.llparser.next_token()

    def _next_token(self, llparser):
        self._tokens_skip(llparser)
        self.token = llparser.next_token()
        if self.token.iserror:
            return ParseError(str(self.token.value),
                              llparser.position, llparser.position)

        if self.token.iseof:
            return ParseError("Unexpected end of file",
                              llparser.position, llparser.position)

        return None

    def do_parse(self, llparser):
        assert llparser is not None

        self.llparser = llparser

        return self.pop_parse(rbp=0)

    def pop_parse(self, rbp):
        err = self._next_token(self.llparser)
        if err is not None:
            return err

        if self.token.token_type not in self.expressions:
            return ParseError("Unexpected token type: "\
                              + self.token.token_type,
                              self.token.start_pos, self.token.end_pos)

        expr = self.expressions[self.token.token_type]

        # advance
        prev_token = self.token

        if expr.isprefix:
            left = expr.parse_prefix(self, prev_token)
            if left.iserror or self.llparser.peek_token().iseof:
                return left
        elif expr.isinfix:
            return ParseError("No left operand in expression",
                              prev_token.start_pos, self.llparser.position)

        # continue, from here we know there is a left operand
        self._tokens_skip(self.llparser)
        self.token = self.llparser.next_token()
        if self.token.iserror:
            return ParseError(str(self.token.content),
                              self.llparser.position, self.llparser.position)

        if self.token.token_type not in self.expressions:
            self.llparser.put_back_token(self.token)
            return left  # end of expression at left

        next_expr = self.expressions[self.token.token_type]

        right_binding_power = rbp
        while True:
            prev_token = self.token

            left = next_expr.parse_infix(self, left, prev_token)
            if self.llparser.peek_token().iseof:
                return left

            err = self._next_token(self.llparser)
            if err is not None:
                return err

            if self.token.token_type not in self.expressions:
                self.llparser.put_back_token(self.token)
                return left

            next_expr = self.expressions[self.token.token_type]

            if (not next_expr.isinfix)\
               or right_binding_power >= next_expr.left_binding_power:
                self.llparser.put_back_token(self.token)
                return left

        # (never) ending while
