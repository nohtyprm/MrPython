from MenuManager import MenuManager
from PyEditorList import PyEditorList
from PyIconFrame import PyIconFrame
from PyShell import PyShell
from tkinter.ttk import *
from tkinter import *

import tkinter.font

class MainView:
    """
    The application window
    Creates the editor and shell interfaces
    """

    def __init__(self, root):
        self.root = root
        self.recent_files_menu = None

        default_font = tkinter.font.nametofont("TkFixedFont")
        default_font.configure(size=12)

        ### XXX : a small hack to use a nicer default theme
        s = Style()
        #print("Themes = {}".format(s.theme_names()))
        import sys
        if sys.platform == 'linux' and 'clam' in s.theme_names():
            s.theme_use('clam')

        self.create_view()

        self.menu_manager = MenuManager(self)
        self.menu_manager.createmenubar()

        self.py_editor_list.set_recent_files_menu(self.recent_files_menu)

    def show(self):
        self.root.mainloop()

    def create_view(self):
        """ Create the window : editor and shell interfaces """
        self.view = PanedWindow(self.root, width=800, height=700,
                                orient=VERTICAL, background="white")
        self.view.pack(fill=BOTH, expand=1)
        self.create_py_icon_frame(self.view)
        self.create_py_editor_list(self.view)
        self.create_py_shell(self.view)

        self.view.add(self.py_icon_frame, minsize=59, height=59)
        self.view.add(self.py_editor_list, height=600)
        self.view.add(self.py_shell.text, height=220)
        self.view.add(self.py_shell.entre, minsize=27, height=27)

    def create_py_icon_frame(self, parent):
        self.py_icon_frame = PyIconFrame(parent)

    def create_py_editor_list(self, parent):
        self.py_editor_list = PyEditorList(parent)

    def create_py_shell(self, parent):
        self.py_shell = PyShell(parent)

