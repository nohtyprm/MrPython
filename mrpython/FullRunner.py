from code import InteractiveInterpreter
from RunReport import RunReport
import ast
import tokenize
import sys
import traceback

class FullRunner:
    """
    Runs a code under the full mode
    """
    
    def __init__(self, filename, source):
        self.filename = filename
        self.source = source
        self.report = RunReport()        


    def get_report(self):
        """ Return the report """
        return self.report


    def execute(self, locals):
        """ Run the code """
        basic_interpreter = InteractiveInterpreter(locals=locals)
        error_output = open('interpreter_error', 'w+')
        original_error = sys.stderr
        sys.stderr = error_output
        try:
            code = compile(self.source, self.filename, 'exec')
        except:
            InteractiveInterpreter.showsyntaxerror(self.filename)
            sys.stderr.seek(0)
            result = sys.stderr.read()
            self.report.set_result(result)
            return False
        else: # No compilation errors here
            result = basic_interpreter.runcode(code)            
            sys.stderr.seek(0)
            result = sys.stderr.read()
            if result:
                self.report.set_result(result)
                return False
            else:
                sys.stdout.seek(0)
                result = sys.stdout.read()
                self.report.set_result(result)
                return True
        finally:
            sys.stderr = original_error
            error_output.close()


    def evaluate(self, expr, locals):
        """ Lanches the evaluation with the locals dict built before """
        basic_interpreter = InteractiveInterpreter(locals=locals)
        error_output = open('interpreter_error', 'w+')
        original_error = sys.stderr
        sys.stderr = error_output
        try:
            code = compile(expr, '<string>', 'eval')
        except:
            InteractiveInterpreter.showsyntaxerror(self.filename)
            sys.stderr.seek(0)
            result = sys.stderr.read()
            self.report.set_result(result)
            return False            
        else:
            try:
                result = eval(code, locals, locals)
            except:
                basic_interpreter.showtraceback()
                sys.stderr.seek(0)
                result = sys.stderr.read()
                self.report.set_result(result)
                return False
            else:
                self.report.set_result(result)
                return True
        finally:
            sys.stderr = original_error
            error_output.close()


