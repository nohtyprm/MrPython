from StudentRunner import StudentRunner
from FullRunner import FullRunner
from translate import tr

import tokenize

class PyInterpreter:
    """
    This class aims at running the code and checking process, and builds
    a report that will be sent to the Console
    """

    def __init__(self, mode, filename, source=None):
        self.filename = filename
        if source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()
        self.source = source
        self.mode = mode
        # This dictionnary can keep the local declarations form the execution of code
        # Will be used for evaluation
        self.locals = dict()


    def run_evaluation(self, expr):
        """ Run the evaluation of expr """
        runner = None
        if self.mode == "student":
            runner = StudentRunner(self.filename, self.source)
        else:
            runner = FullRunner(self.filename, self.source)

        ok = runner.evaluate(expr, self.locals)
        report = runner.get_report()
        begin_report = "=== " + tr("Evaluating: ") + "'" + expr[:-1] + "' ===\n"
        report.set_header(begin_report)
        end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
        report.set_footer(end_report)

        return (ok, report)

    def execute(self):
        """ Execute the runner corresponding to the chosen Python mode """
        runner = None
        if self.mode == "student":
            runner = StudentRunner(self.filename, self.source)
        else:
            runner = FullRunner(self.filename, self.source)

        ok = runner.execute(self.locals)

        report = runner.get_report()
        import os
        begin_report = "=== " + tr("Interpretation of: ") + "'" + os.path.basename(self.filename) + "' ===\n"
        report.set_header(begin_report)
        end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
        report.set_footer(end_report)

        return (ok, report)
