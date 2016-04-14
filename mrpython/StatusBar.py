from tkinter import *
from platform import python_version

class StatusBar(Frame):
    """
    Manages the status bar that give some information about the current
    environment and editor
    """

    def __init__(self, parent, notebook):
        Frame.__init__(self, parent, background="#e1e1e1")
        self.UPDATE_PERIOD = 100
        self.config(borderwidth=1, relief=GROOVE)
        self.python_label = Label(self, text="Python " + python_version(),
                                  borderwidth=1, relief=RAISED,
                                  background="#e1e1e1")
        self.position_label = Label(self, text="position", borderwidth=1,
                                    relief=RAISED, justify=RIGHT,
                                    background="#e1e1e1", width=10)
        self.python_label.pack(side=RIGHT, ipadx=8, ipady=3)
        self.position_label.pack(side=RIGHT, ipadx=8, ipady=3)
        self.notebook = notebook
        self.update_position()

    
    def update_position(self):
        """ Update the position displayed in the status bar, corresponding
            to the cursor position inside the current editor """
        position = ''
        if self.notebook.index("end") > 0:
            index = self.notebook.get_current_editor().index(INSERT)
            line, col = index.split('.')
            position = "Li " + line + ", Col " + col
        self.position_label.config(text=position)
        self.after(self.UPDATE_PERIOD, self.update_position)
