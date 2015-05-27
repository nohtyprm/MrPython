from code import InteractiveInterpreter
import tokenize
import subprocess
import sys
import linecache
import time
import socket
import rpc
from configHandler import idleConf
import tkinter.messagebox as tkMessageBox

class MyRPCClient(rpc.RPCClient):

    def handle_EOF(self):
        "Override the base class - just re-raise EOFError"
        raise EOFError

class ModifiedInterpreter(InteractiveInterpreter):

    def __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.save_warnings_filters = None
        self.restarting = False
        self.subprocess_arglist = None
        self.original_compiler_flags = self.compile.compiler.flags


    rpcclt = None

    def execfile(self, filename, source=None):
        "Execute an existing file"
        if source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()
        try:
            code = compile(source, filename, "exec")
        except (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            print('*** Error in script or command!\n'
                 'Traceback (most recent call last):',
                  file=self.tkconsole.stderr)
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        else:
            self.runcode(code)

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

    def runcode(self, code):
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

