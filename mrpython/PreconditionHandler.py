import ast
import inspect
import re

# This class is made to update precondition nodes to match them with
# the right line
# Not updating could mismatch traceback lineno with the expected precondition line
class PreconditionAstLinenoUpdater(ast.NodeVisitor):

    def __init__(self, lineno):
        self.lineno = lineno

    def visit(self, node):
        if hasattr(node, 'lineno'):
            node.lineno = self.lineno
        if hasattr(node, 'end_lineno'):
            node.end_lineno = self.lineno
        self.generic_visit(node)

class PreconditionErrorMessageHandler:

    def __init__(self, msg_pattern, traceback, code):
        self.msg = ""
        self.pattern = msg_pattern
        self.tb = traceback
        self.code = code

    # not finished yet
    def build_message(self):
        self.msg = ""
        if len(self.tb) > 1:
            _, lineno, _, line = self.tb[-1]
            func_name = self.tb[-1].name
            assert_lineno = self.tb[-2].lineno
            code_tb = self.tb[-2].line
            arg_names = []
            arg_values = []

            source_code = inspect.getsource(self.code)
            matches = matches = re.findall(r'\((.*?)\)', code_tb)

            try:
                tree = ast.parse(source_code)
            except SyntaxError:
                print("Erreur de syntaxe dans le code fourni.")
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for argg in node.args.args:
                        arg_name = argg.arg
                        arg_names.append(arg_name)

            for match in matches:
                arg_values = match.split(',')

            if len(arg_names) == len(arg_names) : 
                arg = "\n"
                for i in range(len(arg_names)):
                    arg += "\t - " + str(arg_names[i]) + " = " + str(arg_values[i]) + "\n"
                arg += "\t"  + tr("in line :") + " " + code_tb
        return self.msg
