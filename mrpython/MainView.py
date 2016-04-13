from PyEditorList import PyEditorList
from PyIconWidget import PyIconWidget
from Console import Console
from PyEditorWidget import PyEditorWidget
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
        self.create_icon_widget(self.view)
        self.create_editor_widget(self.view)
        self.create_console(self.view)
        # Packing
        self.view.pack(fill=BOTH, expand=1)
        self.icon_widget.pack(fill=BOTH)
        self.editor_widget.pack(fill=BOTH, expand=1)
        self.console.frame_output.pack(fill=BOTH)
        self.console.frame_input.pack(fill=BOTH)


    def create_icon_widget(self, parent):
        """ Create the icon menu on the top """
        self.icon_widget = PyIconWidget(parent, self.root)


    def create_editor_widget(self, parent):
        """ Create the editor area : notebook, line number widget """
        self.editor_widget = PyEditorWidget(parent)


    def create_console(self, parent):
        """ Create the interactive interface in the bottom """
        self.console = Console(parent, self.app)

