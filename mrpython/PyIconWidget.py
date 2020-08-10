from tkinter import *

from translate import tr
from tooltip import ToolTip

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
        # self.config(borderwidth=1, relief=GROOVE)
        # Loading icon pictures
        icon_new_file_gif = PhotoImage(file=expand_filename("icons/new_file_icon4.gif"))
        icon_save_gif = PhotoImage(file=expand_filename("icons/save_icon2.gif"))
        icon_open_gif = PhotoImage(file=expand_filename("icons/open_icon2.gif"))
        icon_tracing_png = PhotoImage(file=expand_filename("icons/tracing_icon.png"))
        self.icon_student_gif = PhotoImage(file=expand_filename("icons/student_icon2.gif"))
        self.icon_pro_gif = PhotoImage(file=expand_filename("icons/pro_icon3.gif"))
        self.icon_run_gif = PhotoImage(file=expand_filename("icons/run_icon2.gif"))
        self.icon_stop_gif = PhotoImage(file=expand_filename("icons/stop_icon2.gif"))

        # Creating the labels
        self.icons = dict()  # dict[str:Label]

        self.icons['new_file'] = ToolTip(Label(self, image=icon_new_file_gif,
                                               cursor="hand1", background="#e1e1e1",
                                               relief="raised", justify=CENTER,
                                               text="", compound=NONE,
                                               activebackground='black'),
                                         msg=tr('New Ctrl-N'))

        self.icons['open'] = ToolTip(Label(self, image=icon_open_gif, justify=CENTER,
                                           cursor="hand1", background="#e1e1e1",
                                           relief="raised", text='',
                                           compound=NONE, activebackground='#A9A9A9'),
                                     msg=tr('Open Ctrl-O'))

        self.icons['save'] = ToolTip(Label(self, image=icon_save_gif, justify=CENTER,
                                           cursor="hand1", background="#e1e1e1",
                                           relief="raised", text='',
                                           compound=NONE, activebackground='#A9A9A9'),
                                     msg=tr('Save Ctrl-S'))

        self.icons['mode'] = ToolTip(Label(self, cursor="hand1", background="#e1e1e1",
                                           relief="raised", justify=CENTER,
                                           text='', compound=NONE,
                                           activebackground='#A9A9A9'),
                                     msg=tr('Mode Ctrl-M'))

        self.icons['run'] = ToolTip(Label(self, image=self.icon_run_gif, justify=CENTER,
                                          cursor="hand1", background="#e1e1e1",
                                          relief="raised", text='',
                                          compound=None, activebackground='#A9A9A9'),
                                    msg=tr('Run Ctrl-R'))

        self.icons['tracing'] = ToolTip(Label(self, image=icon_tracing_png, justify=CENTER,
                                              cursor="hand1", background="#e1e1e1",
                                              relief="raised", text='',
                                              compound=None, activebackground='#A9A9A9'),
                                        msg=tr('Enable/Disable Tracing'))

        # Set the icons inside the labels
        self.icons['new_file'].wdgt.image = icon_new_file_gif
        self.icons['save'].wdgt.image = icon_save_gif
        self.icons['open'].wdgt.image = icon_open_gif
        self.icons['mode'].wdgt.image = self.icon_student_gif
        self.icons['run'].wdgt.image = self.icon_run_gif
        self.icons['tracing'].wdgt.image = icon_tracing_png

        # Packing the labels
        sep = Label(self, background="white")
        sep.grid(row=0, column=0, ipadx=7, ipady=3)
        self.icons['new_file'].wdgt.grid(row=0, column=1, ipadx=7,
                                         ipady=3)
        self.icons['open'].wdgt.grid(row=0, column=2, ipadx=7,
                                     ipady=3)
        self.icons['save'].wdgt.grid(row=0, column=3, ipadx=7,
                                     ipady=3)
        sep = Label(self, background="white")
        sep.grid(row=0, column=4, ipadx=7, ipady=3)
        self.icons['mode'].wdgt.grid(row=0, column=5, ipadx=7,
                                     ipady=3)
        sep = Label(self, background="white")
        sep.grid(row=0, column=6, ipadx=7, ipady=3)
        self.icons['run'].wdgt.grid(row=0, column=7, ipadx=7,
                                    ipady=3)
        sep = Label(self, background="white")
        sep.grid(row=0, column=8, ipadx=60, ipady=3)
        self.icons['tracing'].wdgt.grid(row=0, column=9, ipadx=7,
                                        ipady=3)

    def enable_icon_running(self):
        self.icons['run'].wdgt.config(image=self.icon_stop_gif)

    def disable_icon_running(self):
        self.icons['run'].wdgt.config(image=self.icon_run_gif)

    def switch_icon_mode(self, mode):
        """ Change icon when switching mode """
        if mode == "student":
            self.icons['mode'].wdgt.config(image=self.icon_student_gif)
        elif mode == "full":
            self.icons['mode'].wdgt.config(image=self.icon_pro_gif)

