from StudentRunner import StudentRunner
from FullRunner import FullRunner
from translate import tr

import multiprocessing as mp

import tkinter as tk

import tokenize

import sys

RUN_POLL_DELAY=250

class InterpreterProxy:
    """
    This is a multiprocessing proxy for the underlying python interpreter.
    """
    def __init__(self, root, mode, filename):
        self.comm, there = mp.Pipe()
        self.process = mp.Process(target=run_process, args=(there, mode, filename))
        self.root = root

    def run_evaluation(self, expr, callback):
        if not self.process.is_alive():
            self.process.start()

        def timer_callback():
            if self.comm.poll():
                ok, report = self.comm.recv()
                callback(ok, report)
            else:
                self.root.after(RUN_POLL_DELAY, timer_callback)
            
        self.comm.send('eval')
        self.comm.send(expr)
        timer_callback()

    def execute(self, callback):
        if not self.process.is_alive():
            self.process.start()

        def timer_callback():
            if self.comm.poll():
                ok, report = self.comm.recv()
                callback(ok, report)
            else:
                self.root.after(RUN_POLL_DELAY, timer_callback)
            
        self.comm.send('exec')
        timer_callback()
            
    def kill(self):
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
            return True
        else:
            return False

def run_process(comm, mode, filename):
    
    root = tk.Tk()
    
    interp = PyInterpreter(root, mode, filename)
    
    def run_loop():
        command = comm.recv()
        if command == 'eval':
            expr = comm.recv()
            ok, report = interp.run_evaluation(expr)
            comm.send((ok, report))
        elif command == 'exec':
            ok, report = interp.execute()
            comm.send((ok, report))

        root.after(10, run_loop)

    root.title(tr("Interpretation."))
    root.after(10, run_loop)
    root.withdraw()
    root.mainloop()
    
        
class PyInterpreter:
    """
    This class aims at running the code and checking process, and builds
    a report that will be sent to the Console
    """

    def __init__(self, root, mode, filename, source=None):
        self.root = root
        self.filename = filename
        self.source = source
        self.mode = mode
        # This dictionnary can keep the local declarations form the execution of code
        # Will be used for evaluation
        self.locals = dict()


    def run_evaluation(self, expr):
        """ Run the evaluation of expr """

        output_file = open('interpreter_output', 'w+')
        original_stdout = sys.stdout
        sys.stdout = output_file
        
        runner = None
        if self.mode == "student":
            runner = StudentRunner(self.root, self.filename, expr)
        else:
            runner = FullRunner(self.filename, expr)

        ok = runner.evaluate(expr, self.locals)
        report = runner.get_report()
        begin_report = "=== " + tr("Evaluating: ") + "'" + expr + "' ===\n"
        report.set_header(begin_report)
        end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
        report.set_footer(end_report)

        sys.stdout = original_stdout
        output_file.close()
        
        return (ok, report)

    def execute(self):
        """ Execute the runner corresponding to the chosen Python mode """
        with tokenize.open(self.filename) as fp:
            source = fp.read()

        output_file = open('interpreter_output', 'w+')
        original_stdout = sys.stdout
        sys.stdout = output_file
            
        runner = None
        if self.mode == "student":
            runner = StudentRunner(self.root, self.filename, source)
        else:
            runner = FullRunner(self.filename, source)

        ok = runner.execute(self.locals)

        report = runner.get_report()
        import os
        begin_report = "=== " + tr("Interpretation of: ") + "'" + os.path.basename(self.filename) + "' ===\n"
        len_begin_report = len(begin_report)

        # enable?
        # if self.mode == 'student':
        #     begin_report += "# Automatic importation of graphic library\n"
        #     begin_report += "from studentlib.gfx.image import (draw_line, draw_triangle, fill_triangle\n"
        #     begin_report += "                                  , draw_ellipse, fill_ellipse\n"
        #     begin_report += "                                  , overlay, underlay)\n"
        #     begin_report += "from studentlib.gfx.img_canvas import show_image\n\n"

        report.set_header(begin_report)
        end_report = "\n" + ('=' * len_begin_report) + "\n\n"
        report.set_footer(end_report)

        sys.stdout = original_stdout
        output_file.close()

        return (ok, report)
