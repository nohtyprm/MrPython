import prog_ast

class TypeConverter:
    """A appeler depuis type_checker"""

    def __init(self, Program):
        print("init")

    def parse(self):
        prog = TypeAST()
        for function in self.functions:
            parseFuncType(self, function)
            # A ajouter qqpart ?
        return Anything


    def parseExpr(self, astNode):
        #anything, alias, file,bool, int, float, number, none, image, str,
        if isinstance(astNode, ENum):
            return NumberType()
        else if isinstance(astNode, EStr):
            return StrType()
        else if isinstance(astNode, ETrue) or isinstance(astNode, EFalse):
            return BoolType()
        else if isinstance(astNode, ENone):
            return NoneType()
        return Anything

    def parseVarType(self, astNode):
        if isinstance(astNode, EVar):
            return TypeVariable()
        return Anything

    def parseFuncType(self, astNode):
        if isinstance(astNode, FunctionDef):
            return FunctionType()
        return Anything
