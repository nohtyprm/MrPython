from tkinter import *
from PyEditorList import PyEditorList

class PyEditorWidget(Frame):
    """
    Represents a tkinter Notebook widget with a bar widget displaying the line
    numbers on the left, and a status bar on the bottom
    """

    def __init__(self, parent):
        Frame.__init__(self, parent, background='#E8E8E8')
        self.UPDATE_PERIOD = 100
        # Holds the text inside the line widget : the text simply
        # contains all the line numbers
        self.line_numbers = ''
        self.py_notebook = PyEditorList(self)
        self.py_notebook.grid(row=0, column=1, sticky=(N, S, E, W))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)




