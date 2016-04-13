from code import InteractiveInterpreter
from EnvironmentNodeVisitor import EnvironmentNodeVisitor
import tokenize
import subprocess
import sys
import linecache
import time
import ast
import socket
import rpc
import re
from configHandler import MrPythonConf
import tkinter.messagebox as tkMessageBox

class MyRPCClient(rpc.RPCClient):

    def handle_EOF(self):
        "Override the base class - just re-raise EOFError"
        raise EOFError

class ModifiedInterpreter(InteractiveInterpreter):
    """
    This class aims at running the code and check syntax, and
    report erros if any in the text shell
    """

    rpcclt = None

    def __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules['__main__'].__dict__
        self.environment = set()
        InteractiveInterpreter.__init__(self, locals=locals)
        self.save_warnings_filters = None
        self.restarting = False
        self.subprocess_arglist = None
        self.original_compiler_flags = self.compile.compiler.flags

    def execfile(self, filename, source=None):
        """ Execute an existing file in full Python mode """
        # TODO: AST + redémarrer l'environment à chaque fois
        if source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()
        try:
            code = compile(source, filename, "exec")
        except: # Compilation error : syntax...
            self.tkconsole.change_text_color("error")
            self.tkconsole.write("\n== Erreur(s) de syntaxe dans le script ==\n")
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.write("== Fin du rapport ==\n")
            self.tkconsole.change_text_color("normal")
        else: # Code execution
            self.tkconsole.change_text_color("run")
            self.tkconsole.write("\n== Exécution de %s ==\n" % (filename))
            InteractiveInterpreter.runcode(self, code)
            self.tkconsole.write("== Fin de l'exécution ==\n")
            self.tkconsole.change_text_color("normal")

    def exec_file_student_mode(self, filename, source=None):
        """ Execute an existing file in student Python mode
            Return True if there is compilation or execution error """
        if source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()
        # Parse the code following the rules given in class
        # that students must respect
        # If correct : compile then run the code
        if not self.parse_student_code(filename, source):
            return self.run_student_code(filename, source)
        return True

    def parse_student_code(self, filename, source):
        """ Parse the code and check if it follows the class rules
            Return true if there is at least one rule not followed
            or a compilation error """
        try:
            tree = ast.parse(source, filename)
        except: # Compilation error : syntax...
            self.tkconsole.change_text_color("error")
            self.tkconsole.write("\n== Erreur(s) de syntaxe dans le script ==\n")
            # TODO: afficher des erreurs plus détaillées pour la compilation
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.write("== Fin du rapport ==\n")
            self.tkconsole.change_text_color("normal")
            return True
        else: # Check if the source code respect the class conventions
            errors = False
            # Put the new names into the environment to delete them later  
            # and get all the lines of the functions          
            function_lines = self.update_environment_names(tree)
            # Check if there are asserts that end the source
            if not self.check_tests(tree):
                if not errors:
                    self.tkconsole.change_text_color("error")
                    self.tkconsole.write("\n== Les conventions du cours ne sont "
                                         "pas respectées ==\n")                    
                    errors = True
                self.tkconsole.write("--> Le code doit terminer par un "
                                     "jeu de tests\n")
            # Check if there are specifications for all the defined functions
            # if not self.check_specifications
            # Check if.....
            if errors:
                self.tkconsole.write("== Fin du rapport ==\n")
            return errors

    def update_environment_names(self, tree):
        """ Get all the names in the code source to remove them from
            the environment later """
        visitor = EnvironmentNodeVisitor()
        visitor.visit(tree)
        self.environment = visitor.name_list
        return visitor.function_lines

    def run_student_code(self, filename, source):
        """ Run the code, giving verbose informations about errors
            that can occur during compilation, or during execution 
            Return true if errors """
        # We first change the output for the compiling and execution messages
        output_file = open('interpreter_output', 'w+')
        original_stdout = self.tkconsole.stdout
        original_stderr = self.tkconsole.stderr
        sys.stderr = output_file
        sys.stdout = output_file
        # All send to the temporary output
        code = compile(source, filename, "exec")
        InteractiveInterpreter.runcode(self, code)
        sys.stderr = original_stderr
        sys.stdout = original_stdout
        # Analyse the output seeking for errors (execution)
        output_file.seek(0)
        result = output_file.read()
        errors = (result.find('Traceback (most recent call last):') > -1)
        if errors: # Error : analyse the output to give details
            self.tkconsole.change_text_color("error")
            self.tkconsole.write("\n== Erreur dans le script ==\n")
            self.display_errors(output_file, filename)
            self.tkconsole.write("== Fin du rapport ==\n")
        else: # No error, just copy the result into the shell
            self.tkconsole.change_text_color("run")
            self.tkconsole.write("\n== Exécution de %s ==\n" % (filename))
            self.tkconsole.write(result)
            self.tkconsole.write("== Fin de l'exécution ==\n")
        self.tkconsole.change_text_color("normal")
        output_file.close()
        return errors

    def display_errors(self, output_file, filename):
        """ Analyse the output and display more verbose details about errors """
        output_file.seek(0)
        line_number = 0
        error_line = ''
        line = ''
        # Read the lines, one after another, detect the most recent call in the
        # traceback : this call holds the error
        while (True):
            line = output_file.readline()
            if line.find(filename) > -1:
                search_line = re.search(r"line (?P<number>\d+)", line)
                line_number = int(search_line.group('number'))
                break
        line = output_file.readline()
        # Get the very last line that describes the error
        while (line != ''):
            error_line = line
            line = output_file.readline()
        # What kind of error is it ?
        #   NameError : name that is not defined
        if 'NameError' in error_line:
            search_name = re.search(r"name '(?P<name>\w+)'", error_line)
            name_error = search_name.group('name')
            self.tkconsole.write("--> Ligne " + str(line_number) +
                                 " : La variable '" + name_error +
                                 "' n'est pas définie.")
        #   ZeroDivisionError 
        elif 'ZeroDivisionError' in error_line:
            self.tkconsole.write("--> Ligne " + str(line_number) +
                                 " : Division par zéro.")
        #   Other runtime error
        else:
            self.tkconsole.write("--> Ligne " + str(line_number) +
                                 " : Erreur lors de l'exécution.")
        self.tkconsole.write("\n")
        return line_number

    def clear_environment(self):
        """ Clear the environment : variables, functions previously added """
        for name in self.environment:
            if (name != 'app') and (name in self.locals):
                del self.locals[name]

    def check_specifications(self, source):
        """ Check if all the functions have a specification """
        

    def check_tests(self, tree):
        """ Check if there are asserts that end the source code
            The tree is the root of program (instance of ast.Module) """ 
        stmt_list = tree.body
        test = False
        for node in stmt_list:
            if not isinstance(node, ast.Assert):
                if test:
                    return False
            else:
                test = True
        return test

    def evaluate(self, expression):
        """ Evaluate the expression in the prompt with the environment built
            by the last code execution """
        try:
            result = eval(expression, globals(), self.locals)
        except SyntaxError: # Syntax error
            self.tkconsole.change_text_color("error")
            self.tkconsole.write("\n== Erreur de syntaxe dans l'expression ==\n")
            InteractiveInterpreter.showsyntaxerror(self)
            self.tkconsole.write("== Fin du rapport ==\n")
            self.tkconsole.change_text_color("normal")
        except: # Other errors that can occur
            self.tkconsole.change_text_color("error")
            self.tkconsole.write("\n== Erreur dans l'évaluation de l'expression ==\n")
            InteractiveInterpreter.showtraceback(self)
            self.tkconsole.write("== Fin du rapport ==\n")
            self.tkconsole.change_text_color("normal")
        else: # Print the result of the evaluation to the console
            self.tkconsole.change_text_color("run")
            self.write("\n== Evaluation de l'expression ==\n")
            # This line is for configure the color of the tag region
            print(result)
            self.write("== Fin de l'evaluation ==\n")
            self.tkconsole.change_text_color("normal")

    def checksyntax(self, pyEditor):
        filename=pyEditor.long_title()
        saved_stream = self.tkconsole.get_warning_stream()
        self.tkconsole.set_warning_stream(self.tkconsole.stderr)
        with open(filename, 'rb') as f:
            source = f.read()
        if b'\r' in source:
            source = source.replace(b'\r\n', b'\n')
            source = source.replace(b'\r', b'\n')
        if source and source[-1] != ord(b'\n'):
            source = source + b'\n'
        editwin = pyEditor
        text = editwin
        text.tag_remove("ERROR", "1.0", "end")
        try:
            # If successful, return the compiled code
            compile(source, filename, "exec")
        except (SyntaxError, OverflowError, ValueError) as value:
            msg = getattr(value, 'msg', '') or value #or "<no detail available>"
            lineno = getattr(value, 'lineno', '') or 1
            offset = getattr(value, 'offset', '') or 0
            if offset == 0:
                lineno += 1  #mark end of offending line
            pos = "0.0 + %d lines + %d chars" % (lineno-1, offset-1)
            editwin.colorize_syntax_error(text, pos)

            self.tkconsole.write("%s\n" % msg)
        finally:
            self.tkconsole.set_warning_stream(saved_stream)
            self.tkconsole.showprompt()

    """def runcode(self, code):
        "Override base class method"
        
        
        if self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        if self.save_warnings_filters is not None:
            warnings.filters[:] = self.save_warnings_filters
            self.save_warnings_filters = None
        try:
            self.tkconsole.beginexecuting()
            exec(code, self.locals)
        except SystemExit:
            if not self.tkconsole.closing:
                if tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    master=self.tkconsole.text):
                    raise
                else:
                    self.showtraceback()
            else:
                raise
        except:
            if self.tkconsole.canceled:
                self.tkconsole.canceled = False
                print("KeyboardInterrupt", file=self.tkconsole.stderr)
            else:
                    self.showtraceback()
        finally:
            try:
                self.tkconsole.endexecuting()
            except AttributeError:  # shell may have closed
                pass
        """

    def showtraceback(self):
        "Extend base class method to reset output properly"
        self.tkconsole.resetoutput()
        self.checklinecache()
        InteractiveInterpreter.showtraceback(self)

    def checklinecache(self):
        c = linecache.cache
        for key in list(c.keys()):
            if key[:1] + key[-1:] != "<>":
                del c[key]

