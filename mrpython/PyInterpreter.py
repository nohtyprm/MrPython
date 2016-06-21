from StudentRunner import StudentRunner
from FullRunner import FullRunner
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
        result = runner.evaluate(expr, self.locals)
        self.report = runner.get_report()
        begin_report = "=== Rapport d'évaluation de '" + expr[:-1] + "' ===\n"
        end_report = "\n=== Fin du rapport d'évaluation ===\n\n"
        if self.mode == "student":
            text, result = self.build_report_text_student()
            return (begin_report + text + end_report, result)
        else:
            if result == True:
                result = 'run'
            else:
                result = 'error'
            return (begin_report + self.build_report_text_full() + end_report, result)
        

    def execute(self):
        """ Execute the runner corresponding to the chosen Python mode """
        runner = None
        if self.mode == "student":
            runner = StudentRunner(self.filename, self.source)
        else:
            runner = FullRunner(self.filename, self.source)
        result = runner.execute(self.locals)
        self.report = runner.get_report()
        begin_report = "=== Rapport d'exécution de " + self.filename + " ===\n"
        end_report = "\n=== Fin du rapport d'exécution ===\n\n"
        if self.mode == "student":
            text, result = self.build_report_text_student()
            return (begin_report + text + end_report, result)
        else:
            if result == True:
                result = 'run'
            else:
                result = 'error'
            return (begin_report + self.build_report_text_full() + end_report, result)


    def build_report_text_student(self):
        """ Build the output text that will be displayed into the Console
            and return it with the status (error, no error) """
        text = ""
        if self.report.compilation_errors:
            error = self.report.compilation_errors
            if error[0] == 'indentation':
                text += "=> Ligne " + str(error[1]) + " : erreur d'indentation"
            elif error[0] == 'syntax':
                text += "=> Ligne " + str(error[1]) + " : erreur de syntaxe\n"
                text = text + str(error[3])
                for i in range(0, error[2] - 1):
                    text += " "
                text += "^"
            return (text, 'error')
        if self.report.convention_errors:
            for error in self.report.convention_errors:
                if error[0] == 'asserts':
                    text += "=> Il n'y a pas de jeu de tests à la fin du code source\n"
                if error[0] == 'specifications':
                    text += "=> Les fonctions doivent avoir des spécifications valides\n"
            return (text, 'error')
        if self.report.execution_errors:
            error = self.report.execution_errors
            if error[0] == 'name':
                text += "=> Ligne " + str(error[1]) + " : la variable '"
                text += str(error[2]) + "' n'est pas définie"
            if error[0] == 'zero_division':
                text += "=> Ligne " + str(error[1]) + " : Division par zéro"
            return (text, 'error')
        # No error
        text += str(self.report.result)
        return (text, 'run')


    def build_report_text_full(self):
        """ Build the output text that will be displayed into the Console
            and return it with the status (error, no error) """
        return str(self.report.result)


