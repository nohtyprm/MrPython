from tkinter import *

import os
MODULE_PATH = os.path.dirname(__file__)

def expand_filename(fname):
    return MODULE_PATH + "/" + fname

class PyIconWidget(Frame):
    """
    Manages the PyIconFrame widget which contains the icons
    """
    def __init__(self, parent, root):
        Frame.__init__(self, parent, background="white")
        #self.config(borderwidth=1, relief=GROOVE)
        # Loading icon pictures
        icon_new_file_gif = PhotoImage(file=expand_filename("icons/new_file_icon.gif"))
        icon_save_gif = PhotoImage(file=expand_filename("icons/save_icon.gif"))
        icon_open_gif = PhotoImage(file=expand_filename("icons/open_icon.gif"))
        self.icon_student_gif = PhotoImage(file=expand_filename("icons/student_icon.gif"))
        self.icon_pro_gif = PhotoImage(file=expand_filename("icons/pro_icon.gif"))
        icon_run_gif = PhotoImage(file=expand_filename("icons/run_icon.gif"))

        # Creating the labels
        self.icons = dict()  # dict[str:Label]

        self.icons['new_file'] = Label(self, image=icon_new_file_gif,
                                       cursor="hand1", background="#e1e1e1", 
                                       relief="raised", justify=CENTER,
                                       text='New  CTRL-N', compound=NONE,
                                       activebackground='black')

        self.icons['save'] = Label(self, image=icon_save_gif, justify=CENTER, 
                                   cursor="hand1", background="#e1e1e1", 
                                   relief="raised", text='Save  CTRL-S',
                                   compound=NONE, activebackground='#A9A9A9')

        self.icons['open'] = Label(self, image=icon_open_gif, justify=CENTER, 
                                   cursor="hand1", background="#e1e1e1", 
                                   relief="raised", text='Open  CTRL-O',
                                   compound=NONE, activebackground='#A9A9A9')
        self.icons['mode'] = Label(self, cursor="hand1", background="#e1e1e1",
                                  relief="raised", justify=CENTER,
                                  text='Mode  CTRL-M', compound=NONE,
                                  activebackground='#A9A9A9')
        self.icons['run'] = Label(self, image=icon_run_gif, justify=CENTER,
                                  cursor="hand1", background="#e1e1e1", 
                                  relief="raised", text='Run  CTRL-R',
                                  compound=NONE, activebackground='#A9A9A9')

        # Set the icons inside the labels
        self.icons['new_file'].image = icon_new_file_gif
        self.icons['save'].image = icon_save_gif
        self.icons['open'].image = icon_open_gif
        self.icons['mode'].image = self.icon_student_gif
        self.icons['run'].image = icon_run_gif

        # Packing the labels
        self.icons['new_file'].grid(row=0, column=0, ipadx=7,
                                    ipady=3)
        self.icons['save'].grid(row=0, column=1, ipadx=7,
                                ipady=3)
        self.icons['open'].grid(row=0, column=2, ipadx=7,
                                ipady=3)
        self.icons['mode'].grid(row=0, column=3, ipadx=7,
                                ipady=3)
        self.icons['run'].grid(row=0, column=4, ipadx=7,
                               ipady=3)

    def show_texts(self):
        for (_, icon) in self.icons.items():
            icon.config(compound=BOTTOM)

    def hide_texts(self):
        for (_, icon) in self.icons.items():
            icon.config(compound=NONE)

    def switch_icon_mode(self, mode):
        """ Change icon when switching mode """
        if mode == "student":
            self.icons['mode'].config(image=self.icon_student_gif)
        elif mode == "full":
            self.icons['mode'].config(image=self.icon_pro_gif)

