
from PyInterpreter import InterpreterProxy

class FileChecker:
    def __init__(self):
        self.interpreter = None
        self.report = None

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



        

