from tkinter import *

class PyIconFrame(Frame):
    """
    Manages the PyIconFrame widget which contains the icons 
    - New File Icon
    - Run Icon
    - Mode Icon (student or full-python mode)
    """
    
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        
        # New File icon
        icon_new_file_gif = PhotoImage(file="new_file_icon.gif")
        self.icon_new_file_label = Label(self, image=icon_new_file_gif, 
                                    cursor="hand1", background="#e1e1e1", 
                                    relief="sunken")
        self.icon_new_file_label.image = icon_new_file_gif
        self.icon_new_file_label.grid(row=0, column=0, padx=3, pady=3, 
                                      ipadx=3, ipady=3)
        
        # Run icon
        icon_run_gif = PhotoImage(file="run_icon.gif")
        self.icon_run_label = Label(self, image=icon_run_gif, 
                                    cursor="hand1", background="#e1e1e1", 
                                    relief="sunken")
        self.icon_run_label.image = icon_run_gif
        self.icon_run_label.grid(row=0, column=1, padx=3, pady=3, 
                                 ipadx=3, ipady=3)

        # Mode icon
        self.icon_student_gif = PhotoImage(file="student_icon.gif")
        self.icon_pro_gif = PhotoImage(file="pro_icon.gif")
        self.icon_mode_label = Label(self, cursor="hand1",
                                     background="#e1e1e1", relief="sunken")
        self.icon_mode_label.grid(row=0, column=3, padx=3, pady=3, 
                                      ipadx=3, ipady=3)
                                      
    def switch_icon_mode(self, mode):
        if mode == "student":
            self.icon_mode_label.config(image=self.icon_student_gif)
        elif mode == "full":
            self.icon_mode_label.config(image=self.icon_pro_gif)
        
        
        
        
        
        
        
        
        
