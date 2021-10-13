from code import InteractiveInterpreter
from RunReport import RunReport
import ast
import tokenize
import sys
import traceback
import os
import copy

from translate import tr

import studentlib.gfx.image
import studentlib.gfx.img_canvas

import typing

from typechecking.typechecker import typecheck_from_ast
from typechecking.type_ast import PREDEFINED_TYPE_VARIABLES

def install_locals(locals):
    # install the gfx lib

    #locals = { k:v for (k,v) in locs.items() }
    locals['draw_line'] = studentlib.gfx.image.draw_line
    locals['line'] = studentlib.gfx.image.draw_line
    locals['draw_triangle'] = studentlib.gfx.image.draw_triangle
    locals['triangle'] = studentlib.gfx.image.draw_triangle
    locals['fill_triangle'] = studentlib.gfx.image.fill_triangle
    locals['filled_triangle'] = studentlib.gfx.image.fill_triangle
    locals['draw_ellipse'] = studentlib.gfx.image.draw_ellipse
    locals['ellipse'] = studentlib.gfx.image.draw_ellipse
    locals['fill_ellipse'] = studentlib.gfx.image.fill_ellipse
    locals['filled_ellipse'] = studentlib.gfx.image.fill_ellipse
    locals['overlay'] = studentlib.gfx.image.overlay
    locals['underlay'] = studentlib.gfx.image.underlay
    locals['empty_image'] = studentlib.gfx.image.empty_image
    locals['show_image'] = studentlib.gfx.img_canvas.show_image

    # install the typing module
    locals['Sequence'] = typing.Sequence
    locals['List'] = typing.List
    locals['Set'] = typing.Set
    locals['Iterable'] = typing.Iterable
    locals['Tuple'] = typing.Tuple
    locals['Dict'] = typing.Dict
    locals['Optional'] = typing.Optional
    locals['Callable'] = typing.Callable

    # hack
    locals['Image'] = None

    for tvar in PREDEFINED_TYPE_VARIABLES:
        locals[tvar] = typing.TypeVar(tvar)

    return locals

class StudentRunner:
    """
    Runs a code under the student mode
    """

    def __init__(self, tk_root, filename, source, check_tk=True):
        self.filename = filename
        self.source = source
        self.AST = None
        self.report = RunReport()
        self.tk_root = tk_root
        self.running = True

        if check_tk:
            ## This is a hack so let's check...
            try:
                self.tk_root.nametowidget('.')
            except:
                raise ValueError("TK Root is not set (please report)")
            

    def get_report(self):
        """ Return the report """
        return self.report


    def execute(self, locals, capture_stdout=True):
        """ Run the file : customized parsing for checking rules,
            compile and execute """
        # Compile the code and get the AST from it, which will be used for all
        # the conventions checkings that need to be done

        try:
            self.AST = ast.parse(self.source, self.filename)
        # Handle the different kinds of compilation errors
        except IndentationError as err:
            self.report.add_compilation_error('error', tr("Bad indentation"), err.lineno, err.offset)
            return False
        except SyntaxError as err:
            self.report.add_compilation_error('error', tr("Syntax error"), err.lineno, err.offset, details=err.text)
            return False
        except Exception as err:
            typ, exc, tb = sys.exc_info()
            self.report.add_compilation_error('error', str(typ), err.lineno, err.offset, details=str(err))
            return False

        # No parsing error here

        # perform the local checks
        ret_val = True
        if not self.check_rules(self.report):
            ret_val = False
            self.run(locals, capture_stdout) # we still run the code even if there is a convention error
        else:
            self.add_FunctionPreconditions()
            ret_val = self.run(locals, capture_stdout) # Run the code if it passed all the convention tests
            if ret_val:
                self.report.nb_passed_tests = self.nb_asserts

        return ret_val

    def _extract_error_details(self, err):
        err_str = err.args[0]
        start = err_str.find("'") + 1
        end = err_str.find("'", start + 1)
        details = err_str[start:end]
        return details

    def _exec_or_eval(self, mode, code, globs, locs):
        assert mode=='exec' or mode=='eval'
        try:
            if mode=='exec':
                result = exec(code, globs, locs)
            elif mode=='eval':
                result = eval(code, globs, locs)
        except TypeError as err:
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            err_str = self._extract_error_details(err)
            self.report.add_execution_error('error', tr("Type error"), lineno, details=str(err))
            return (False, None)
        except NameError as err:
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            err_str = self._extract_error_details(err)
            self.report.add_execution_error('error', tr("Name error (unitialized variable?)"), lineno, details=err_str)
            return (False, None)
        except ZeroDivisionError:
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            self.report.add_execution_error('error', tr("Division by zero"), lineno if mode=='exec' else None)
            return (False, None)
        except AssertionError:
            a, b, tb = sys.exc_info()
            lineno=None
            traceb = traceback.extract_tb(tb)
            if len(traceb) > 1:
                filename, lineno, file_type, line = traceb[-1]
            if lineno in preconditionsLineno:
                self.report.add_execution_error('error', tr("Precondition error (False)"), lineno)
            else:
                self.report.add_execution_error('error', tr("Assertion error (failed test?)"), lineno)
            return (True, None)
        except Exception as err:
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            lineno=None
            traceb = traceback.extract_tb(tb)
            if len(traceb) > 1:
                filename, lineno, file_type, line = traceb[-1]
            else:
                self.report.add_execution_error('error', a.__name__, lineno, details=str(err))
            return (False, None)
        finally:
            self.running = False

        return (True, result)


    def run(self, locals, capture_stdout=True):
        """ Run the code, add the execution errors to the rapport, if any """
        locals = install_locals(locals)
        code = None
        try:
            code = compile(self.AST, self.filename, 'exec')
        except SyntaxError as err:
            self.report.add_compilation_error('error', tr("Syntax error"), err.lineno, err.offset, details=str(err))
            return False
        except Exception as err:
            typ, exc, tb = sys.exc_info()
            self.report.add_compilation_error('error', str(typ), err.lineno, err.offset, details=str(err))
            return False

        (ok, result) = self._exec_or_eval('exec', code, locals, locals)
        #if not ok:
        #    return False

        # if no error get the output
        if capture_stdout:
            sys.stdout.seek(0)
            result = sys.stdout.read()
            self.report.set_output(result)

        return ok


    def evaluate(self, expr, locals):
        """ Launches the evaluation with the locals dict built before """
        locals = install_locals(locals)
        (ok, result) = self._exec_or_eval('eval', expr, locals, locals)
        if not ok:
            return False
        else:
            sys.stdout.seek(0)
            outp = sys.stdout.read()
            self.report.set_output(outp)
            self.report.set_result(result)
            return True

    def check_rules(self, report):
        """ Check if the code follows the class rules """
        if not self.check_asserts():
            return False
        if not self.check_specifications():
            return False

        if not self.check_types():
            return False

        return True

    def check_specifications(self):
        """ Is there a valid specification for each function ? """
        # Put the checking code here
        return True


    def check_asserts(self):
        """ Are there asserts at the end of the source code ? """
        self.nb_asserts = 0
        defined_funs = set()
        funcalls = set()
        for node in self.AST.body:
            #print("node: {}".format(node))
            if isinstance(node, ast.Assert):
                #print("assert found: {}".format(node))
                call_visit = FunCallsVisitor()
                call_visit.visit(node)
                self.nb_asserts += 1
                funcalls.update(call_visit.funcalls)
            elif isinstance(node, ast.FunctionDef):
                defined_funs.add(node.name)

        #print("defined funs = {}".format(defined_funs))
        #print("funcalls = {}".format(funcalls))

        self.report.nb_defined_funs = len(defined_funs)

        missing = defined_funs.difference(funcalls)

        if missing:
            self.report.add_convention_error('warning', tr('Missing tests')
                                             , details="\n" + tr('Untested functions: ')
                                             + "{}".format(missing) + "\n")
        elif defined_funs:
            # all the functions are tested at least once
            self.report.add_convention_error('run', tr('All functions tested'), details="==> " + tr("All functions tested (good)"))

        return True

    def check_types(self):
        type_ctx = typecheck_from_ast(self.AST, self.filename, self.source)
        fatal_error = False
        if len(type_ctx.type_errors) == 0:
            # no type error
            self.report.add_convention_error('run', tr('Program type-checked'), details=tr('==> the program is type-checked (very good)\n'))
            return True

        # convert type errors to report messages
        for type_error in type_ctx.type_errors:
            type_error.report(self.report)
            if type_error.is_fatal():
                fatal_error = True

        #print("fatal_error = ", str(fatal_error))
        return not fatal_error

    def add_FunctionPreconditions(self):
        self.AST = FunctionDefVisitor().visit(self.AST)
        ast.fix_missing_locations(self.AST)

class FunCallsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.funcalls = set()

    def visit_children(self, node):
        super(FunCallsVisitor, self).generic_visit(node)

    def visit_Call(self, node):
        if hasattr(node.func, "id"):
            #print("Function name = {}".format(node.func.id))
            self.funcalls.add(node.func.id)
        self.visit_children(node)

from typechecking.typechecker import preconditions

preconditionsLineno = []

class FunctionDefVisitor(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        if node.name not in preconditions or len(preconditions[node.name]) == 0:
            return node
        else:
            ast_asserts = []
            for precondition_node in preconditions[node.name]:
                lineno = precondition_node.lineno
                preconditionsLineno.append(lineno)
                assert_node = ast.Assert(precondition_node)
                assert_node.lineno = lineno
                ast_asserts.append(assert_node)
            if hasattr(node, "type_comment"):
                node_res = ast.FunctionDef(node.name,node.args,ast_asserts+node.body,node.decorator_list,node.returns,node.type_comment,lineno = node.lineno,col_offset = node.col_offset, end_lineno = node.lineno, end_col_offset = node.end_col_offset)
            else: # python 3.7
                node_res = ast.FunctionDef(node.name,node.args,ast_asserts+node.body,node.decorator_list,node.returns,lineno = node.lineno,col_offset = node.col_offset, end_lineno = node.lineno)
            return node_res

        
if __name__ == "__main__":
    # for testing purpose only
    runner = StudentRunner(None, "toto.py","""
def f(a : int, b : int) -> int:
    \"\"\"
    précondition :
        a > b and a > 0
    \"\"\"
    return a - b

print(f(2,1))
""", check_tk=False)

    runner.execute(dict(), capture_stdout=False)
