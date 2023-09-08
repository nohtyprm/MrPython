
from PyInterpreter import InterpreterProxy

import typechecking.prog_ast as prog_ast
import typechecking.typechecker as typechecker
from RunReport import RunReport

class FileChecker:
    def __init__(self):
        self.interpreter = None
        self.report = None

    def check(self, filename):
        report = RunReport()
        prog = prog_ast.Program()
        prog.build_from_file(filename)
        ctx = prog.type_check()
        if ctx.type_errors:
           for error in ctx.type_errors:
               error.report(report)

        return report


    def run(self, filename):
        """ Check and run the program in the current editor : execute, print results """
        self.interpreter = InterpreterProxy(None, 'student', filename)
        
        callback_called = False
        
        # the call back
        def callback(ok, report):
            # XXX: the ok is not trustable
            if report.has_compilation_error() or report.has_execution_error():
                ok = False

            nonlocal callback_called
            if callback_called:
                return
            else:
                callback_called = True

            self.interpreter.kill()
            self.interpreter = None

            self.report = report


        # non-blocking call
        self.interpreter.execute(callback)

        while self.report is None:
            sleep(0.250)

        return self.report



        

