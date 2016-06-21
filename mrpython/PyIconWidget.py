from tkinter import *

class PyIconWidget(Frame):
    """
    Manages the PyIconFrame widget which contains the icons
    """
    
    def __init__(self, parent, root):
        Frame.__init__(self, parent, background="white")
        #self.config(borderwidth=1, relief=GROOVE)
        # Loading icon pictures
        icon_new_file_gif = PhotoImage(file="new_file_icon.gif")        
        icon_save_gif = PhotoImage(file="save_icon.gif")
        icon_open_gif = PhotoImage(file="open_icon.gif")
        self.icon_student_gif = PhotoImage(file="student_icon.gif")
        self.icon_pro_gif = PhotoImage(file="pro_icon.gif")
        icon_run_gif = PhotoImage(file="run_icon.gif")
        # Creating the labels
        self.icon_new_file_label = Label(self, image=icon_new_file_gif,
                                         cursor="hand1", background="#e1e1e1", 
                                         relief="raised", justify=CENTER,
                                         text='New  CTRL-N', compound=BOTTOM,
                                         activebackground='black')
        self.icon_save_label = Label(self, image=icon_save_gif, justify=CENTER, 
                                     cursor="hand1", background="#e1e1e1", 
                                     relief="raised", text='Save  CTRL-S',
                                     compound=BOTTOM, activebackground='#A9A9A9')
        self.icon_open_label = Label(self, image=icon_open_gif, justify=CENTER, 
                                     cursor="hand1", background="#e1e1e1", 
                                     relief="raised", text='Open  CTRL-O',
                                     compound=BOTTOM, activebackground='#A9A9A9')
        self.icon_mode_label = Label(self, cursor="hand1", background="#e1e1e1",
                                     relief="raised", justify=CENTER,
                                     text='Mode  CTRL-M', compound=BOTTOM,
                                     activebackground='#A9A9A9')
        self.icon_run_label = Label(self, image=icon_run_gif, justify=CENTER,
                                    cursor="hand1", background="#e1e1e1", 
                                    relief="raised", text='Run  CTRL-R',
                                    compound=BOTTOM, activebackground='#A9A9A9')
        # Set the icons inside the labels
        self.icon_new_file_label.image = icon_new_file_gif
        self.icon_save_label.image = icon_save_gif
        self.icon_open_label.image = icon_open_gif
        self.icon_mode_label.image = self.icon_student_gif
        self.icon_run_label.image = icon_run_gif
        # Packing the labels
        self.icon_new_file_label.grid(row=0, column=0, ipadx=7,
                                      ipady=3)
        self.icon_save_label.grid(row=0, column=1, ipadx=7,
                                  ipady=3)
        self.icon_open_label.grid(row=0, column=2, ipadx=7,
                                  ipady=3)
        self.icon_mode_label.grid(row=0, column=3, ipadx=7,
                                  ipady=3)
        self.icon_run_label.grid(row=0, column=4, ipadx=7,
                                 ipady=3)

                    
    def switch_icon_mode(self, mode):
        """ Change icon when switching mode """
        if mode == "student":
            self.icon_mode_label.config(image=self.icon_student_gif)
        elif mode == "full":
            self.icon_mode_label.config(image=self.icon_pro_gif)

