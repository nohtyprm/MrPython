from platform import python_version
from tkinter import *
from WidgetRedirector import WidgetRedirector
from InterpreterServer.RunServer import RunServer
import uuid
from multiprocessing import Process, Pipe
import socket

import version
from translate import tr
import io
import rpc
import time
import tokenize
import json


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
        Starts the RunServer and connects to it
        """
        self.app = app
        # Creating output console
        self.frame_output = Frame(output_parent)
        self.scrollbar = Scrollbar(self.frame_output)
        self.scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.output_console = ReadOnlyText(self.frame_output, height=15, 
                                   yscrollcommand=self.scrollbar.set)
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

        #AJOUT
        self.interpreter = Process(target=RunServer)
        self.interpreter.start()
        time.sleep(1)
        self._connect_server()
        self.session_id = None
        self.prot = None

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
        #self.interpreter = None


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
        #self.switch_input_status(False)

    def write_report(self, status, report):
        tag = 'run'
        if not status:
            tag = 'error'

        self.write(report.header, tags=(tag))
        if not status:
            for error in report.convention_errors:
                self.write(str(error), tags=(error.severity))
            for error in report.compilation_errors:
                self.write(str(error), tags=(error.severity))
            for error in report.execution_errors:
                self.write(str(error), tags=(error.severity))
        else:
            self.write(str(report.output), tags=('stdout'))
            if report.result is not None:
                self.write(repr(report.result), tags=('normal'))

        self.write(report.footer, tags=(tag))


    def evaluate_action(self, *args):
        """ Sends the expression in the input_console for the server to evaluate it; waits for the result and displays it"""
        #output_file = open('interpreter_output', 'w+')
        #original_stdout = sys.stdout
        #sys.stdout = output_file
        expr = self.input_console.get()
        while expr and (expr[0] == "\n"):
             expr = expr[1:]
        result = self._compute_json(expr, "", self.app.mode, "eval")   
        docJson = json.dumps(result)
        self.mySocket.send(docJson.encode("Utf8"))

        msgServeur=self.mySocket.recv(1024).decode("Utf8")
        if(not msgServeur):
            self.mySocket.close()
            return
        prot = json.loads(msgServeur)

        if prot["msg_type"] == "eval_success":
            self.input_history.record(expr)

        self.input_console.delete(0, END)
        self.write_report2(prot)

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

    def close_server(self):
        '''
        Closes connection with the server
        '''
        self.mySocket.close()

    def _connect_server(self):
        '''
        Connects to the server
        '''
        HOST = socket.gethostname()
        mon_fichier_config = open("config.txt", "r")
        PORT = int(mon_fichier_config.read())

        # 1) création du socket :
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
        # 2) envoi d'une requête de connexion au serveur :
        try:
            self.mySocket.connect((HOST, PORT))
        except socket.error:
            sys.exit()

    def _compute_json(self, source, filename, mode, exec_or_eval):
        '''
        Creates the message that will be sent to the server
        '''
        result = {}
        if(exec_or_eval == "exec"):
            self.session_id = uuid.uuid1().int
            id_exec2 = uuid.uuid1().int
            result = {"session_id" : self.session_id, "msg_id" : id_exec2,
                      "msg_type" : exec_or_eval, "protocol_version" : 0.1,
                      "content" : {"source" : source, "mode" : mode, "filename" :filename}}
        elif (exec_or_eval == "eval"):
            id_exec2 = uuid.uuid1().int
            if(self.session_id == None):
                self.session_id = uuid.uuid1().int
            result = {"session_id" : self.session_id, "msg_id" : id_exec2,
                      "msg_type" : exec_or_eval, "protocol_version" : 0.1,
                      "content" : {"expr" : source, "mode" : mode, "filename" : filename}}
        elif(exec_or_eval == "interrupt"):
            id_exec2 = uuid.uuid1().int
            result = {"session_id" : self.session_id, "msg_id" : id_exec2,
                      "msg_type" : exec_or_eval, "protocol_version" : 0.1, "content" : {}}
        return result

    def write_report2(self, prot):
        '''
        Writes a report in the output console
        '''
        if(prot == {}):
            self.write("===========================\n", tags=('error'))
            self.write("fichier de sortie trop gros\n", tags=("normal"))
            self.write("===========================\n", tags = ('error'))
        elif(prot["msg_type"] == "exec_success" or prot["msg_type"] == "eval_success" ):
            self.write(prot["content"]["report"]["header"], tags=('run'))
            for i in prot["content"]["report"]["errors"]:
                self.write(i["infos"]["severity"]+ ": line "+str(i["infos"]["severity"]))
                self.write(str(i["infos"]["description"]),tags=(i["infos"]["severity"]))
            self.write(str(prot["content"]["stdout"]), tags=("stdout"))
            if(prot["msg_type"] == "eval_success" and prot["content"]["data"] != None):
                self.write(prot["content"]["data"], tags=('stdout'))
            self.write(prot["content"]["report"]["footer"], tags = ('run'))
        elif(prot["msg_type"] == "interrupt_success"):
            self.write("==========================================\n", tags=('run'))
            self.write("le programme a été correctement interrompu\n", tags=("normal"))
            self.write("==========================================\n", tags = ('run'))
        else:
            self.write(prot["content"]["report"]["header"], tags=('error'))
            for i in prot["content"]["report"]["errors"]:
                self.write(i["infos"]["severity"]+ ": line "+str(i["infos"]["lines"]), tags=(i["infos"]["severity"]))
                self.write(str(i["infos"]["description"]),tags=(i["infos"]["severity"]))
            self.write(prot["content"]["report"]["footer"], tags = ('error'))


    def run(self, filename):

        """Sends a program for the server to run it; waits for the result and displays it"""
        # Reset the output first
        self.reset_output()
        # A new PyInterpreter is created each time code is run
        # It is then kept for other actions, like evaluation
        # self.interpreter = PyInterpreter(self.app.mode, filename)
        with tokenize.open(filename) as fp:
                source = fp.read()
        result = self._compute_json(source, filename, self.app.mode, "exec")
        docJson = json.dumps(result)
        self.wait, send = Pipe()

        self.mySocket.send(docJson.encode("Utf8"))
        self.procwait = Process(target=self.wait_and_write, args=(send,))
        self.procwait.start()
        intepreted = False
        for i in range(20):
            if(self.wait.poll(0.5)):
                self.prot = self.wait.recv()
                self.write_report2(self.prot)
                intepreted = True
                break
        if(not intepreted):
            self.app.icon_widget.switch_icon_exec(True) #Modifie le bouton
            self.app.run_button.bind("<1>", self.app.interrupt) #change le bind

    def interrupt(self):
        """ Sends and interrupt request to the server
        Changes the execution button and writes a message on the output_console when it's done
        """
        result = self._compute_json("","","","interrupt")
        docJson = json.dumps(result)
        self.mySocket.send(docJson.encode("Utf8"))
        self.procwait.join()
        self.app.run_button.bind("<1>", self.app.run_module)
        self.app.icon_widget.switch_icon_exec(False)
        self.prot = self.wait.recv()
        if(self.prot != None):
            self.write_report2(self.prot)

    def no_file_to_run_message(self):
        self.reset_output()
        self.write("=== No file to run ===", "error")


    def write(self, s, tags=()):
        """ Write into the output console """
        if (isinstance(s, str) and len(s) and max(s) > '\uffff'):
            # Tk doesn't support outputting non-BMP characters
            # Let's assume what printed string is not very long,
            # find first non-BMP character and construct informative
            # UnicodeEncodeError exception.
            for start, char in enumerate(s):
                if (char > '\uffff'):
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

    def wait_and_write(self, pipe):
        """Awaits an answer from the server and registers it"""
        msgServeur = self.mySocket.recv(1024).decode("Utf8")
        if(not msgServeur):
            self.mySocket.close()
            return
        try: # The buffer is not enough big
            prot = json.loads(msgServeur)
            pipe.send(prot)
        except:
            try:
                self.mySocket.setblocking(False)
                while(True):
                    data = self.mySocket.recv(1024).decode("Utf8")
                    if(data == None):
                        break

            except:
                self.mySocket.setblocking(True)
                prot = json.loads("{}")
                pipe.send(prot)
                return
        

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
