from platform import python_version
from tkinter import *
from tkinter.font import Font, nametofont
from PyInterpreter import InterpreterProxy
from WidgetRedirector import WidgetRedirector

from HyperlinkManager import HyperlinkManager

import version
from translate import tr
import io
import rpc

class ConsoleHistory:
    def __init__(self, history_capacity=100):
        assert history_capacity > 0
        assert history_capacity < 10000
        self.history_capacity = history_capacity
        self.clear()

    def record(self, txt):
        #print("[History] record: " + txt)
        if not txt:
            return

        if self.history_size == self.history_capacity:
            self.history = self.history[1:]
            self.history_size -= 1

        self.history.append(txt)
        self.history_size += 1
        self.history_pos = self.history_size - 1

        #print(self)

    def move_past(self):
        if self.history_pos > 0:
            entry = self.history[self.history_pos]
            self.history_pos -= 1
            # print("[Move past]: " + entry)
            # print(self)

            return entry
        elif self.history_pos == 0:
            entry = self.history[self.history_pos]
            # print("[Move past] (last): " + entry)
            # print(self)

            return entry
        else:
            # print("[Move past]: no history...")
            # print(self)
            return None

    def move_future(self):
        if self.history_pos < self.history_size - 1:
            self.history_pos += 1
            entry = self.history[self.history_pos]
            # print("[Move future]: " + entry)
            # print(self)
            return entry
        elif self.history_pos == self.history_size - 1:
            # print("[Move future]: last...")
            # print(self)
            return ""
        else:
            # print("[Move future]: no history...")
            # print(self)
            return None

    def clear(self):
        self.history = []
        self.history_size = 0
        self.history_pos = -1

    def __str__(self):
        str = "History:["
        i = 0
        for entry in self.history:
            if i == self.history_pos:
                str += "<"
            str += "'{}'".format(entry)
            if i == self.history_pos:
                str += ">"

            if i < self.history_size:
                str += ", "

            i += 1

        str += "]"

        return str


class ErrorCallback:
    def __init__(self, src, error):
        self.src = src
        self.error = error

    def __call__(self):
        print("error line=" + str(self.error.line))
        self.src.app.goto_position(self.error.line, self.error.offset or 0)


# from: http://tkinter.unpythonic.net/wiki/ReadOnlyText
class ReadOnlyText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

class Console:
    """
    Interactive console of MrPython, consisting of two widgets : output and input
    """

    from ModifiedColorDelegator import ModifiedColorDelegator
    from ModifiedUndoDelegator import ModifiedUndoDelegator
    from IdleHistory import History

    SHELL_TITLE = "Python " + python_version() + " Shell"
    TEXT_COLORS_BY_MODE = {
                            'run':'green',
                            'error':'red',
                            'normal':'black',
                            'warning':'orange'
                          }

    def __init__(self, output_parent, input_parent, app):
        """
        Create and configure the shell (the text widget that gives informations
        and the interactive shell)
        """
        self.app = app
        # Creating output console
        self.frame_output = Frame(output_parent)
        self.scrollbar = Scrollbar(self.frame_output)
        self.scrollbar.grid(row=0, column=1, sticky=(N, S))



        self.output_console = ReadOnlyText(self.frame_output, height=15, 
                                   yscrollcommand=self.scrollbar.set)

        self.hyperlinks = HyperlinkManager(self.output_console)

        self.frame_output.config(borderwidth=1, relief=GROOVE)
        self.output_console.grid(row=0, column=0, sticky=(N, S, E, W))
        self.scrollbar.config(command=self.output_console.yview)

        self.frame_output.rowconfigure(0, weight=1)
        self.frame_output.columnconfigure(0, weight=1)

        # Creating input console
        self.frame_input = Frame(input_parent)
        self.arrows = Label(self.frame_input, text=" >>> ")
        self.input_console = Entry(self.frame_input, background='#775F57',
                                  #height=1,
                                   state='disabled', relief=FLAT)
        self.input_console.bind('<Return>', self.evaluate_action)
        self.input_history = ConsoleHistory()
        self.input_console.bind('<Up>', self.history_up_action)
        self.input_console.bind('<Down>', self.history_down_action)
        #self.frame_input.config(borderwidth=1, relief=GROOVE)
        self.eval_button = Button(self.frame_input, text="Eval",
                                  command=self.evaluate_action, width=7,
                                  state='disabled')
        self.arrows.config(borderwidth=1, relief=RIDGE)
        self.arrows.grid(row=0, column=0)
        self.input_console.grid(row=0, column=1, sticky="ew")
        self.eval_button.grid(row=0, column=2)

        self.frame_input.columnconfigure(1, weight=1)

	# Redirect the Python output, input and error stream to the console
        import IOBinding
        self.stdin = PseudoInputFile(self, "error", IOBinding.encoding)
        self.stdout = PseudoOutputFile(self, "error", IOBinding.encoding)
        self.stderr = PseudoOutputFile(self, "error", IOBinding.encoding)
        self.console = PseudoOutputFile(self, "error", IOBinding.encoding)
        #sys.stdout = self.stdout
        #sys.stderr = self.stderr
        #sys.stdin = self.stdin
        # The current Python mode 
        self.mode = "student"

        self.reading = False
        self.executing = False
        self.canceled = False
        self.endoffile = False
        self.closing = False
        self._stop_readling_flag = False

        self.history = self.History(self.output_console)
        self.undo = undo = self.ModifiedUndoDelegator()
        self.io = IOBinding.IOBinding(self)
        self.begin()
        self.configure_color_tags()
        self.switch_input_status(True)
        self.interpreter = None

    def change_font(self, nfont):
        self.output_console.configure(font=nfont)
        self.input_console.configure(font=nfont)

    def configure_color_tags(self):
        """ Set the colors for the specific tags """
        self.output_console.tag_config('run', foreground='green')
        self.output_console.tag_config('error', foreground='red')
        self.output_console.tag_config('normal', foreground='black')
        self.output_console.tag_config('warning', foreground='orange')
        self.output_console.tag_config('stdout', foreground='gray')


    def reset_output(self):
        """ Clear all the output console """
        #self.output_console.config(state=NORMAL)
        self.output_console.delete(1.0, END)
        self.begin()

        self.write("MrPython v.{} -- mode {}\n".format(version.version_string(),
                                                       tr(self.mode)))
        #self.output_console.config(state=DISABLED)


    def change_mode(self, mode):
        """ When the mode change : clear the output console and display
            the new mode """
        self.mode = mode
        self.reset_output()
        self.hyperlinks.reset()
        #self.switch_input_status(False)

    def write_report(self, status, report):
        tag = 'run'
        if not status:
            tag = 'error'

        self.hyperlinks.reset()

        self.write(report.header, tags=(tag))
        for error in report.convention_errors:
            hyper, hyper_spec = self.hyperlinks.add(ErrorCallback(self, error))
            print("hyper={}".format(hyper))
            print("hyper_spec={}".format(hyper_spec))
            self.write(str(error), tags=(error.severity, hyper, hyper_spec))
            self.write("\n")

        if not status:
            for error in report.compilation_errors:
                def error_click_cb():
                    self.app.goto_position(error.line, error.offset)
                    hyper, hyper_spec = self.hyperlinks.add(ErrorCallback(self, error))
                self.write(str(error), tags=(error.severity, hyper, hyper_spec))
            for error in report.execution_errors:
                def error_click_cb():
                    self.app.goto_position(error.line, error.offset)
                    hyper, hyper_spec = self.hyperlinks.add(ErrorCallback(self, error))
                self.write(str(error), tags=(error.severity, hyper, hyper_spec))
        else:
            for error in report.execution_errors:
                def error_click_cb():
                    self.app.goto_position(error.line, error.offset)
                    hyper, hyper_spec = self.hyperlinks.add(ErrorCallback(self, error))
                self.write(str(error), tags=(error.severity, hyper, hyper_spec))

            self.write(str(report.output), tags=('stdout'))
            if report.result is not None:
                self.write(repr(report.result), tags=('normal'))

        self.write(report.footer, tags=(tag))

    def evaluate_action(self, *args):
        """ Evaluate the expression in the input console """
        expr = self.input_console.get()
        local_interpreter = False
        if self.interpreter is None:
            self.interpreter = InterpreterProxy(self.app.root, self.app.mode, "<<console>>")
            local_interpreter = True
            self.app.running_interpreter_proxy = self.interpreter

        callback_called = False

        # the call back
        def callback(ok, report):
            nonlocal callback_called
            if callback_called:
                return
            else:
                callback_called = True

            if ok:
                self.input_history.record(expr)

            self.input_console.delete(0, END)
            self.write_report(ok, report)

            if local_interpreter:
                self.interpreter.kill()
                self.interpreter = None
                self.app.running_interpreter_proxy = None

            self.app.icon_widget.disable_icon_running()
            self.app.running_interpreter_callback = None

        # non-blocking call
        self.app.icon_widget.enable_icon_running()
        self.app.running_interpreter_callback = callback
        self.interpreter.run_evaluation(expr, callback)

    def history_up_action(self, event=None):
        entry = self.input_history.move_past()
        if entry is not None:
            self.input_console.delete(0, END)
            self.input_console.insert(0, entry)

    def history_down_action(self, event=None):
        entry = self.input_history.move_future()
        if entry is not None:
            self.input_console.delete(0, END)
            self.input_console.insert(0, entry)

    def switch_input_status(self, on):
        """ Enable or disable the evaluation bar and button """
        stat = None
        bg = None
        if on:
            stat = 'normal'
            bg = '#FFA500'
        else:
            stat = 'disabled'
            bg = '#775F57'
        self.input_console.config(state=stat, background=bg)
        self.eval_button.config(state=stat)
        
    def run(self, filename):
        """ Run the program in the current editor : execute, print results """
        # Reset the output first
        self.reset_output()
        # A new PyInterpreter is created each time code is run
        # It is then kept for other actions, like evaluation
        if self.interpreter is not None:
            self.interpreter.kill()
            self.app.running_interpreter_proxy = None

            
        self.interpreter = InterpreterProxy(self.app.root, self.app.mode, filename)
        self.app.running_interpreter_proxy = self.interpreter

        callback_called = False
        
        def callback(ok, report):
            nonlocal callback_called
            if callback_called:
                return
            else:
                callback_called = True

            #print("[console] CALLBACK: exec ok ? {}  report={}".format(ok, report))
            self.write_report(ok, report)

            # Enable or disable the evaluation bar according to the execution status
            if ok:
                self.input_console.focus_set()
                #self.switch_input_status(True)
            else:
                # kill the interpreter
                self.interpreter.kill()
                self.interpreter = None
                self.app.running_interpreter_proxy = None
                

            self.app.icon_widget.disable_icon_running()
            self.app.running_interpreter_callback = None
                
        # non-blocking call
        self.app.icon_widget.enable_icon_running()
        self.app.running_interpreter_callback = callback
        self.interpreter.execute(callback)

    def no_file_to_run_message(self):
        self.reset_output()
        self.write("=== No file to run ===", "error")


    def write(self, s, tags=()):
        """ Write into the output console """
        if isinstance(s, str) and len(s) and max(s) > '\uffff':
            # Tk doesn't support outputting non-BMP characters
            # Let's assume what printed string is not very long,
            # find first non-BMP character and construct informative
            # UnicodeEncodeError exception.
            for start, char in enumerate(s):
                if char > '\uffff':
                    break
            raise UnicodeEncodeError("UCS-2", char, start, start+1,
                                     'Non-BMP character not supported in Tk')
        try:
            self.output_console.mark_gravity("iomark", "right")
            if isinstance(s, (bytes, bytes)):
                s = s.decode(IOBinding.encoding, "replace")
            #self.output_console.configure(state='normal')
            self.output_console.insert("iomark", s, tags)
            #self.output_console.configure(state='disabled')
            self.output_console.see("iomark")
            self.output_console.update()
            self.output_console.mark_gravity("iomark", "left")
        except:
            raise
        if self.canceled:
            self.canceled = 0
            raise KeyboardInterrupt


    def begin(self):
        """ Display some informations in the output console at the beginning """
        self.output_console.mark_set("iomark", "insert")
        sys.displayhook = rpc.displayhook
        self.write("Python %s on %s\n" %
                   (sys.version, sys.platform))


    def readline(self):
        save = self.READING
        try:
            self.READING = 1
        finally:
            self.READING = save
        if self._stop_readline_flag:
            self._stop_readline_flag = False
            return ""
        line = self.output_console.get("iomark", "end-1c")
        if len(line) == 0:  # may be EOF if we quit our mainloop with Ctrl-C
            line = "\n"
        self.reset_output()
        if self.canceled:
            self.canceled = 0
            raise KeyboardInterrupt
        if self.endoffile:
            self.endoffile = 0
            line = ""
        return line


    def reset_undo(self):
        self.undo.reset_undo()


class PseudoFile(io.TextIOBase):

    def __init__(self, shell, tags, encoding=None):
        self.shell = shell
        self.tags = tags
        self._encoding = encoding


    @property
    def encoding(self):
        return self._encoding


    @property
    def name(self):
        return '<%s>' % self.tags


    def isatty(self):
        return True


class PseudoOutputFile(PseudoFile):

    def writable(self):
        return True


    def write(self, s):
        if self.closed:
            raise ValueError("write to closed file")
        if type(s) is not str:
            if not isinstance(s, str):
                raise TypeError('must be str, not ' + type(s).__name__)
            # See issue #19481
            s = str.__str__(s)
        return self.shell.write(s, self.tags)


class PseudoInputFile(PseudoFile):

    def __init__(self, shell, tags, encoding=None):
        PseudoFile.__init__(self, shell, tags, encoding)
        self._line_buffer = ''


    def readable(self):
        return True


    def read(self, size=-1):
        if self.closed:
            raise ValueError("read from closed file")
        if size is None:
            size = -1
        elif not isinstance(size, int):
            raise TypeError('must be int, not ' + type(size).__name__)
        result = self._line_buffer
        self._line_buffer = ''
        if size < 0:
            while True:
                line = self.shell.readline()
                if not line: break
                result += line
        else:
            while len(result) < size:
                line = self.shell.readline()
                if not line: break
                result += line
            self._line_buffer = result[size:]
            result = result[:size]
        return result


    def readline(self, size=-1):
        if self.closed:
            raise ValueError("read from closed file")
        if size is None:
            size = -1
        elif not isinstance(size, int):
            raise TypeError('must be int, not ' + type(size).__name__)
        line = self._line_buffer or self.shell.readline()
        if size < 0:
            size = len(line)
        eol = line.find('\n', 0, size)
        if eol >= 0:
            size = eol + 1
        self._line_buffer = line[size:]
        return line[:size]


    def close(self):
        self.shell.close()
