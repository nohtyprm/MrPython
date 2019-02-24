from code import InteractiveInterpreter
from RunReport import RunReport
import ast
import tokenize
import sys
import traceback

import tempfile

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


    def execute_or_eval(self, mode, locals):
        """ Run the code """
        basic_interpreter = InteractiveInterpreter(locals=locals)

        with tempfile.TemporaryFile(mode='w+', prefix='interpreter_error') as error_output:
        
            original_error = sys.stderr
            sys.stderr = error_output
            try:
                if mode == 'exec':
                    code = compile(self.source, self.filename, 'exec')
                else:
                    code = compile(self.expr, '<string>', 'eval')
            except:
                InteractiveInterpreter.showsyntaxerror(self.filename)
                sys.stderr.seek(0)
                result = sys.stderr.read()
                self.report.add_compilation_error('error', err_type='SyntaxError', details=result)
                return False
            else: # No compilation errors here
                if mode == 'exec':
                    result = basic_interpreter.runcode(code)

                    sys.stderr.seek(0)
                    result = sys.stderr.read()
                    if result:
                        self.report.add_compilation_error('error', err_type='SyntaxError', details=result)
                        return False
                    else:
                        sys.stdout.seek(0)
                        result = sys.stdout.read()
                        self.report.set_result(result)
                        return True

                else: # mode eval
                    try:
                        result = eval(code, locals, locals)
                    except Exception as err:
                        a, b, tb = sys.exc_info() # Get the traceback object
                        # Extract the information for the traceback corresponding to the error
                        # inside the source code : [0] refers to the result = exec(code)
                        # traceback, [1] refers to the last error inside code
                        filename, lineno, file_type, line = traceback.extract_tb(tb)[1]
                        print(traceback.format_exception(a, b, tb))
                        tb_str = "".join(traceback.format_exception_only(a, b))
                        self.report.add_execution_error('error', a.__name__, details=str(err))
                        return False

                    self.report.set_result(result)
                    return True

            finally:
                sys.stderr = original_error

    def execute(self, locals):
        """ Run the code """
        return self.execute_or_eval('exec', locals)

    def evaluate(self, expr, locals):
        """ Lanches the evaluation with the locals dict built before """
        self.expr = expr
        result = self.execute_or_eval('eval', locals)
        self.expr = None
        return result

