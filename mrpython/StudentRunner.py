from code import InteractiveInterpreter
from RunReport import RunReport
import ast
import tokenize
import sys
import traceback

from translate import tr

import studentlib.gfx.image
import studentlib.gfx.img_canvas

def install_locals(locals):
    #locals = { k:v for (k,v) in locs.items() }
    locals['draw_line'] = studentlib.gfx.image.draw_line
    locals['draw_triangle'] = studentlib.gfx.image.draw_triangle
    locals['fill_triangle'] = studentlib.gfx.image.fill_triangle
    locals['draw_ellipse'] = studentlib.gfx.image.draw_ellipse
    locals['fill_ellipse'] = studentlib.gfx.image.fill_ellipse
    locals['overlay'] = studentlib.gfx.image.overlay
    locals['underlay'] = studentlib.gfx.image.underlay
    locals['show_image'] = studentlib.gfx.img_canvas.show_image
    return locals


class StudentRunner:
    """
    Runs a code under the student mode
    """

    def __init__(self, filename, source):
        global TK_ROOT
        self.filename = filename
        self.source = source
        self.report = RunReport()
        self.tk_root = TK_ROOT
        self.running = True
        ## This is a hack so let's check...
        try:
            self.tk_root.nametowidget('.')
        except e:
            raise ValueError("TK Root is not set (please report)")


    def get_report(self):
        """ Return the report """
        return self.report


    def execute(self, locals):
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

        # No compilation error here

        # perform the local checks
        if not self.check_rules(self.report):
            return False
        else:
            return self.run(locals) # Run the code if it passed all the convention tests

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
            self.report.add_execution_error('error', tr("Assertion error (failed test?)"), lineno)
            return (False, None)
        except Exception as err:
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            lineno=None
            traceb = traceback.extract_tb(tb)
            if len(traceb) > 1:
                filename, lineno, file_type, line = traceb[-1]
            self.report.add_execution_error('error', a.__name__, lineno, details=str(err))
            return (False, None)
        finally:
            self.running = False

        return (True, result)


    def run(self, locals):
        """ Run the code, add the execution errors to the rapport, if any """
        locals = install_locals(locals)
        code = compile(self.source, self.filename, 'exec')

        (ok, result) = self._exec_or_eval('exec', code, locals, locals)
        if not ok:
            return False

        # if no error get the output
        sys.stdout.seek(0)
        result = sys.stdout.read()
        self.report.set_output(result)

        return True


    def evaluate(self, expr, locals):
        """ Lanches the evaluation with the locals dict built before """
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
        return True

    def check_specifications(self):
        """ Is there a valid specification for each function ? """
        # Put the checking code here
        return True


    def check_asserts(self):
        """ Are there asserts at the end of the source code ? """
        # TODO : a finer check is needed
        return True
        # stmt_list = self.AST.body
        # test = False
        # for node in stmt_list:
        #     if not isinstance(node, ast.Assert):
        #         if test:
        #             test = False
        #     else:
        #         test = True
        # if not test:
        #     self.report.asserts_not_valid()
        #     return False
        # else:
        #     return True


