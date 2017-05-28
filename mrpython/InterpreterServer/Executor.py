'''
Created on 27 avr. 2017

@author: 3301202
'''
import traceback
import sys
from InterpreterServer.RunReport import RunReport
from InterpreterServer.Parser import Parser
from InterpreterServer.Compiler import Compiler
from InterpreterServer.translate import tr

class Executor(object):
    '''
    Execution and evaluation class
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.locals = {} 
        self.fst_stdout = None
        self.fst_stderr = None

    def _extract_error_details(self, err):
        err_str = err.args[0]
        start = err_str.find("'") + 1
        end = err_str.find("'", start + 1)
        details = err_str[start:end]
        return details

    def execute(self, code, report, exe):
        '''
        Execute or evaluate the code
        returns stdin, stdout and if it's an evaluation, returns data
        '''
        self.std_redirect()
        try:
            if(exe):
                exec(code, self.locals, self.locals)
            else:
                eval(code, self.locals, self.locals)
        except TypeError as err:
            self.std_reset()
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            err_str = self._extract_error_details(err)
            report.add_execution_error('error', tr("Type error"), lineno, details=str(err))
            return (report, None, None, True)
        except NameError as err:
            self.std_reset()
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            err_str = self._extract_error_details(err)
            report.add_execution_error('error', tr("Name error (unitialized variable?)"),
                                       lineno, details=err_str)
            return (report, None, None, True)
        except ZeroDivisionError:
            self.std_reset()
            a, b, tb = sys.exc_info()
            filename, lineno, file_type, line = traceback.extract_tb(tb)[-1]
            report.add_execution_error('error', tr("Division by zero"), lineno)
            return (report, None, None, True)
        except AssertionError:
            self.std_reset()
            a, b, tb = sys.exc_info()
            lineno = None
            traceb = traceback.extract_tb(tb)
            if len(traceb) > 1:
                filename, lineno, file_type, line = traceb[-1]
            report.add_execution_error('error', tr("Assertion error (failed test?)"), lineno)
            return (report, None, None, True)
        except Exception as err:
            self.std_reset()
            a, b, tb = sys.exc_info() # Get the traceback object
            # Extract the information for the traceback corresponding to the error
            # inside the source code : [0] refers to the result = exec(code)
            # traceback, [1] refers to the last error inside code
            lineno = None
            traceb = traceback.extract_tb(tb)
            if (len(traceb) > 1):
                filename, lineno, file_type, line = traceb[-1]
            report.add_execution_error('error', a.__name__, lineno, details=str(err))
            return (report, None,None,True)
        sys.stdout.seek(0) #remise à zero des deux fichier afin de les lires
        sys.stderr.seek(0)
        out_string = sys.stdout.read() # calcul de la sortie
        err_string = sys.stderr.read()
        self.std_reset()
        if(not exe):
            return(report, out_string, err_string, False)
        else:
            return(report, out_string, err_string, False)

    def std_redirect(self):
        self.fst_stdout = sys.stdout
        self.fst_stderr = sys.stderr
        sys.stdout = open("out.txt", 'w+')
        sys.stderr = open("err.txt", 'w+')

    def std_reset(self):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.fst_stdout
        sys.stderr = self.fst_stderr
