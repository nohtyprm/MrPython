from code import InteractiveInterpreter
from RunReport import RunReport
import ast
import tokenize
import sys
import traceback

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
            self.report.add_compile_error('indentation', err.lineno, err.offset)
            return False
        except SyntaxError as err:
            self.report.add_compile_error('syntax', err.lineno, err.offset, err.text)
            return False
        else: # No compilation errors here
            # Check whether the source code respects the class conventions
            if self.check_rules():
                self.run(locals) # Run the code if it passed all the convention tests
                return True
            else:
                return False

    def run(self, locals):
        """ Run the code, add the execution errors to the rapport, if any """
        locals = install_locals(locals)
        code = compile(self.source, self.filename, 'exec')
        try:
            result = exec(code, locals, locals)
        except NameError as err:
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            filename, lineno, file_type, line = traceback.extract_tb(tb)[1]
            err_str = err.args[0]
            start = err_str.find("'") + 1
            end = err_str.find("'", start + 1)
            name = err_str[start:end]
            self.report.add_execution_error('name', lineno, details=name)
        except ZeroDivisionError:
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[1]
            self.report.add_execution_error('zero_division', lineno)
        else:
            sys.stdout.seek(0)
            result = sys.stdout.read()
            self.report.set_result(result)


    def evaluate(self, expr, locals):
        """ Lanches the evaluation with the locals dict built before """
        locals = install_locals(locals)
        try:
            result = eval(expr, locals, locals)
        except IndentationError as err:
            self.report.add_compile_error('indentation', err.lineno, err.offset)
            return False
        except SyntaxError as err:
            self.report.add_compile_error('syntax', err.lineno, err.offset, err.text)
            return False
        except NameError as err:
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            filename, lineno, file_type, line = traceback.extract_tb(tb)[1]
            err_str = err.args[0]
            start = err_str.find("'") + 1
            end = err_str.find("'", start + 1)
            name = err_str[start:end]
            self.report.add_execution_error('name', lineno, details=name)
        except ZeroDivisionError:
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[1]
            self.report.add_execution_error('zero_division', lineno)
        else:
            self.report.set_result(result)

    def check_rules(self):
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


