from tkinter import *
from platform import python_version

class StatusBar(Frame):
    """
    Manages the status bar that gives some information about the current
    environment and editor
    """

    # TODO: add the labels for:
    #   - the current mode
    #   - a save label (like gedit)

    def __init__(self, parent, notebook):
        Frame.__init__(self, parent, background="#e1e1e1", padx=20)
        self.UPDATE_PERIOD = 100
        self.config(borderwidth=1, relief=GROOVE)
        self.python_label = Label(self, text="Python " + python_version(),
                                  borderwidth=1, relief=FLAT, width=13,
                                  background="#e1e1e1", foreground="#101010")
        self.position_label = Label(self, text="position", borderwidth=1,
                                    relief=FLAT, justify=CENTER, width=13,
                                    background="#e1e1e1", foreground="#101010")
        self.mode_label = Label(self, text="", borderwidth=1, relief=FLAT,
                                justify=CENTER, background="#e1e1e1", width=13,
                                foreground="#101010")
        self.python_label.pack(side=RIGHT, ipadx=8, ipady=3)
        self.position_label.pack(side=RIGHT, ipadx=8, ipady=3)
        self.mode_label.pack(side=RIGHT, ipadx=8, ipady=3)
        self.notebook = notebook
        self.update_position()

    
    def update_position(self):
        """ Update the position displayed in the status bar, corresponding
            to the cursor position inside the current editor """
        position = 'No file'
        if self.notebook.index("end") > 0:
            index = self.notebook.get_current_editor().index(INSERT)
            line, col = index.split('.')
            position = "Li " + line + ", Col " + col
        self.position_label.config(text=position)
        self.after(self.UPDATE_PERIOD, self.update_position)


    def change_mode(self, mode):
        """ Change the current mode displayed in the mode_label """
        display_text = ""
        if mode == "full":
            display_text = "Full python"
        else:
            display_text = "Student python"
        self.mode_label.config(text=display_text)
        
