# import prog_ast
# import type_ast
# from pprint import pprint

try:
    from .type_ast import *
except ImportError:
    from type_ast import *
try:
    from .prog_ast import *
except ImportError:
    from prog_ast import *


class TypeConverter():
    def __init__(self):
        self.stats = {"import": [], "from": []}

    def parse(self, prog):
        print("Création typeAst")
        for assign in prog.global_vars:
            self.visit_Node(assign)

    def visit_Node(self, node):
        # print("-- " + str(type(node)) + "\n")
        if isinstance(node, ETrue) or isinstance(node, EFalse):
            return self.visit_Boolean()
        elif isinstance(node, ENum):
            return self.visit_Integer()
        elif isinstance(node, Assign):
            return self.visit_Assign(node)
        elif isinstance(node, EVar):
            return self.visit_Variable(node)
        # else:
        #     print("UnsupportedNode : " + str(type(node)) + "\n")

    def visit_Variable(self, node):
        #return self.parse_Annotation(self, node.ast.annotation)
        return TypeVariable(self, node.name)

    def visit_Boolean(self):
        print("Creation BoolType\n")
        return BoolType()

    def visit_Integer(self):
        print("Creation IntType\n")
        return IntType()

    def visit_Assign(self, node):
        print("Visit AssignType\n")
        if hasattr(node.ast, "annotation"):
            self.parse_Annotation(node.ast.annotation)
        else:
            print("non")
        self.visit_Node(node.target)

    def parse_Annotation(self, annotation):
        if annotation.id == "int":
            return self.visit_Integer()
        elif annotation.id == "bool":
            return self.visit_Boolean()


if __name__ == "__main__":
    import sys
    import prog_ast
    import type_ast
    prog1 = Program()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "../../examples/revstr.py"

    prog1.build_from_file(filename)

    converter = TypeConverter()
    typeAst = converter.parse(prog1)
