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
        left_frame = Frame(self, background='#E8E8E8')
        empty_frame_space = Frame(left_frame, background='#E8E8E8', height=28,
                                  borderwidth=0, relief=FLAT)
        # Creates the widget (a text one) that displays the line numbers
        self.line_widget = Text(left_frame, width=4, padx=4, state='disabled', 
                                takefocus=0, bd=0, background='#E8E8E8',
                                foreground='#404040', relief=FLAT,
                                borderwidth=0)
        empty_frame_space.grid(row=0, column=0)
        self.line_widget.grid(row=1, column=0, sticky=(N, S))
        left_frame.grid(row=0, column=0, sticky=(N, S))
        left_frame.rowconfigure(1, weight=1)
        self.py_notebook.grid(row=0, column=1, sticky=(N, S, E, W))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.update_line_numbers()


    def get_line_numbers(self):
        """ Get the string that will fill the line widget """
        s = ''
        lineMask = '    %s\n'
        text = self.py_notebook.get_current_editor()
        # First, make sure that the first line is clearly visible within the
        # text widget
        # ll, cc = text.index('@0,0').split('.')
        text.see(text.index('@0,0'))
        # Get the first and last visible lines
        ll, cc = text.index('@0,0').split('.')
        first = ll
        ll, cc = text.index('@0,%d' % text.winfo_height()).split('.')
        last = ll
        # Build the string containing all the line numbers
        for line in range(int(first), int(last) + 1):
            s += (lineMask % line)[-5:]
        return s


    def update_line_numbers(self):
        """ Update the line numbers only if there is at least one file open """
        if self.py_notebook.index("end") > 0:
            text = self.py_notebook.get_current_editor()
            ll, cc = text.index('@0,0').split('.')
            line_numbers = self.get_line_numbers()
            if self.line_numbers != line_numbers:
                self.line_numbers = line_numbers
                self.line_widget.config(state='normal')
                self.line_widget.delete('1.0', END)
                self.line_widget.insert('1.0', self.line_numbers)
                self.line_widget.config(state='disabled')
        else: # No tab -> disable the line widget
                self.line_widget.config(state='normal')
                self.line_widget.delete('1.0', END)
                self.line_widget.config(state='disabled')            
        # Will update again the line widget in UPDATE_PERIOD ms
        self.after(self.UPDATE_PERIOD, self.update_line_numbers)

