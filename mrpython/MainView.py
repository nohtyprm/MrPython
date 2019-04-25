from PyEditorList import PyEditorList
from PyIconWidget import PyIconWidget
from Console import Console
from PyEditorWidget import PyEditorWidget
from StatusBar import StatusBar
from tkinter.ttk import *
from tkinter import *
import sys
import tkinter.font

class MainView:
    """
    The application window
    Creates the editor and shell interfaces
    """

    def __init__(self, app):
        self.root = app.root
        self.app = app
        # Set the font size
        tkinter.font.nametofont("TkFixedFont").configure(size=12)
        # A small hack to use a nicer default theme
        s = Style()
        if sys.platform == 'linux' and 'clam' in s.theme_names():
            s.theme_use('clam')
        self.create_view()


    def show(self):
        """ Main loop of program """
        self.root.mainloop()


    def create_view(self):
        """ Create the window : editor and shell interfaces, menus """
        self.view = Frame(self.root, background="white", width=900)
        # Create the widgets

        # 1) the toolbar
        self.create_icon_widget(self.view)
        self.icon_widget.grid(row=0, column=0, sticky=(W, E))

        # 2) editor and output
        pw = PanedWindow(self.view, orient=VERTICAL, showhandle=True)
        self.create_editor_widget(pw)
        pw.add(self.editor_widget, height=350)

        # 3) console (with output and input)
        self.create_console(pw, self.view)
        self.editor_widget.console = self.console # XXX: a little bit hacky...

        pw.add(self.console.frame_output)
        
        pw.grid(row=1, column=0, sticky=(N, S, E, W))

        self.console.frame_input.grid(row=2, column=0, sticky=(E, W))

        # 4) status bar

        self.create_status_bar(self.view, self.editor_widget.py_notebook)
        self.status_bar.grid(row=3, column=0, sticky=(E, W))

        self.view.rowconfigure(1, weight=1)
        self.view.columnconfigure(0, weight=1)
        self.view.pack(fill=BOTH, expand=1)

    def create_status_bar(self, parent, notebook):
        """ Create the status bar on the bottom """
        self.status_bar = StatusBar(parent, notebook)

    def create_icon_widget(self, parent):
        """ Create the icon menu on the top """
        self.icon_widget = PyIconWidget(parent, self.root)

    def create_editor_widget(self, parent):
        """ Create the editor area : notebook, line number widget """
        self.editor_widget = PyEditorWidget(parent)

    def create_console(self, output_parent, input_parent):
        """ Create the interactive interface in the bottom """
        self.console = Console(output_parent, input_parent, self.app)

