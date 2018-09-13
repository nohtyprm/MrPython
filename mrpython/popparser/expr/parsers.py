'''Expression parsers.

Created on 25 august 2012

@author: F. Peschanski
'''

from popparser import ParseError


#==============================================================================
# BASE EXPRESSION PARSER
#==============================================================================

class Expression:
    def __init__(self, rbp):
        self.right_binding_power = rbp

    @property
    def token_type(self):
        raise NotImplementedError("Abstract method")

    @property
    def isprefix(self):
        return False

    @property
    def isinfix(self):
        return False


#==============================================================================
# PARSERS IN PREFIX POSITION
#==============================================================================

class Prefix(Expression):
    def __init__(self, prio):
        Expression.__init__(self, rbp=prio)

    @property
    def isprefix(self):
        return True

    @property
    def priority(self):
        return self.right_binding_power

    def parse_prefix(self, pop_parser, token):
        argument = pop_parser.pop_parse(rbp=self.right_binding_power)
        if argument.iserror:
            return argument
        return self.on_prefix(token, argument)

    def on_prefix(self, token, argument, start_pos, end_pos):
        raise NotImplementedError("Abstract method")


class Atom(Expression):
    def __init__(self):
        Expression.__init__(self, rbp=0)

    @property
    def isprefix(self):
        return True

    def parse_prefix(self, _, token):
        return self.on_atom(token)

    def on_atom(self, token):
        raise NotImplementedError("Abstract method")


class Bracket(Expression):
    def __init__(self, open_token, close_token):
        Expression.__init__(self, 0)
        self.open_token = open_token
        self.close_token = close_token

    @property
    def isprefix(self):
        return True

    @property
    def token_type(self):
        return self.open_token

    def parse_prefix(self, pop_parser, _):
        expr = pop_parser.pop_parse(rbp=self.right_binding_power)
        if expr.iserror:
            return expr
        pop_parser.consume_token(self.close_token)
        return expr


class Embed(Expression):
    def __init__(self, parser):
        Expression.__init__(self, rbp=0)
        self.parser = parser
        self.expr_parser = None

    @property
    def isprefix(self):
        return True

    def parse_prefix(self, pop_parser, token):
        if token.token_type != self.parser.token_type:
            return ParseError("Mismatch token type '{0}' expecting: {1}"\
                            .format(token.token_type, self.parser.token_type),
                              token.start_pos, token.start_pos)
        pop_parser.llparser.put_back_token(token)
        self.expr_parser = pop_parser
        result = self.parser.parse(pop_parser.llparser)
        self.expr_parser = None
        return result


#==============================================================================
# PARSERS IN INFIX POSITION
#==============================================================================

class InfixGen(Expression):
    def __init__(self, assoc, lbp, rbp):
        assert assoc == 'LEFT' or assoc == 'RIGHT' or assoc == 'NOASSOC'
        # note: non-associative (NONASSOC) operators are behaving like LEFT but
        # the parser can exploit the associativity marker, eg. when building
        # the AST.
        Expression.__init__(self, rbp)
        self.assoc = assoc
        self.left_binding_power = lbp

    @property
    def isinfix(self):
        return True

    def parse_infix(self, pop_parser, left, token):
        if self.assoc == 'RIGHT':
            precedence = self.left_binding_power - 1
        else:  # LEFT or NONASSOC
            precedence = self.right_binding_power

        right = pop_parser.pop_parse(rbp=precedence)
        if right.iserror:
            return right
        return self.on_infix(left, token, right)

    def on_infix(self, left, token, right):
        raise NotImplementedError("Abstract method")


class Infix(InfixGen):
    def __init__(self, assoc, prio):
        InfixGen.__init__(self, assoc, prio, prio)

    @property
    def priority(self):
        return self.right_binding_power


#==============================================================================
# PARSERS IN MIXFIX (PREFIX/INFIX) POSITION
#==============================================================================


class MixfixGen(Expression):
    def __init__(self, prefix_rbp, infix_assoc, infix_lbp, infix_rbp):
        assert infix_assoc == 'LEFT' or infix_assoc == 'RIGHT'\
            or infix_assoc == 'NONASSOC'
        Expression.__init__(self, rbp=prefix_rbp)
        self.prefix_rbp = prefix_rbp
        self.infix_rbp = infix_rbp
        self.infix_lbp = infix_lbp
        self.left_binding_power = infix_lbp
        self.infix_assoc = infix_assoc

    @property
    def isprefix(self):
        return True

    @property
    def isinfix(self):
        return True

    def parse_prefix(self, pop_parser, token):
        argument = pop_parser.pop_parse(rbp=self.prefix_rbp)
        if argument.iserror:
            return argument
        return self.on_prefix(token, argument)

    def on_prefix(self, token, argument):
        raise NotImplementedError("Abstract method")

    def parse_infix(self, pop_parser, left, token):
        if self.infix_assoc == 'RIGHT':
            precedence = self.infix_lbp - 1
        else:  # LEFT or NONASSOC
            precedence = self.infix_rbp

        right = pop_parser.pop_parse(rbp=precedence)
        if right.iserror:
            return right
        return self.on_infix(left, token, right)

    def on_infix(self, left, token, right):
        raise NotImplementedError("Abstract method")


class Mixfix(MixfixGen):
    def __init__(self, prefix_prio, infix_assoc, infix_prio):
        MixfixGen.__init__(self, prefix_prio,
                           infix_assoc, infix_prio, infix_prio)

    @property
    def prefix_priority(self):
        return self.prefix_rbp

    @property
    def infix_priority(self):
        return self.infix_lbp

