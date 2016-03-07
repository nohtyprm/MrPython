from tkinter import *

class ToolTip:
    """
    Create a tooltip for the specified icon label
    """

    def __init__(self, icon_label, text, column):
        self.icon_label = icon_label
        self.text = text
        self.icon_label.bind("<Enter>", self.inside)
        self.icon_label.bind("<Leave>", self.outside)
        self.column = column
        self.tooltip = None

    def inside(self, event=None):
        """
        Create the tooltip when mouse is over the icon
        """
        if (self.tooltip):
            return
        
        x, y, tx, ty = self.icon_label.bbox("insert")
        x += self.icon_label.winfo_rootx()
        y += self.icon_label.winfo_rooty() + 55
        if (self.column % 2 == 1):
            y -= 17
        self.tooltip = Toplevel(self.icon_label)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tooltip, text=self.text, justify='left',
                         background='#ffff99', relief='solid', borderwidth=1,
                         font=("times", "8", "normal"))
        label.pack(ipadx=1)

    def outside(self, event=None):
        """
        Destroy the tooltip when the cursor leaves the icon
        """
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        

class PyIconFrame(Frame):
    """
    Manages the PyIconFrame widget which contains the icons 
    - New File Icon
    - Run Icon
    - Mode Icon (student or full-python mode)
    """
    
    def __init__(self, parent, root):
        Frame.__init__(self, parent, background="white")
        
        # New File icon
        icon_new_file_gif = PhotoImage(file="new_file_icon.gif")
        self.icon_new_file_label = Label(self, image=icon_new_file_gif, 
                                    cursor="hand1", background="#e1e1e1", 
                                    relief="sunken")
        self.icon_new_file_label.image = icon_new_file_gif
        self.icon_new_file_label.grid(row=0, column=0, padx=3, pady=3, 
                                      ipadx=3, ipady=3)
        self.icon_new_file_tooltip = ToolTip(self.icon_new_file_label,
                                             "New file  Ctrl-N", 0)
        
        # Run icon
        icon_run_gif = PhotoImage(file="run_icon.gif")
        self.icon_run_label = Label(self, image=icon_run_gif, 
                                    cursor="hand1", background="#e1e1e1", 
                                    relief="sunken")
        self.icon_run_label.image = icon_run_gif
        self.icon_run_label.grid(row=0, column=1, padx=3, pady=3, 
                                 ipadx=3, ipady=3)
        self.icon_run_tooltip = ToolTip(self.icon_run_label,
                                        "Run  Ctrl-R", 1)

        # Mode icon
        self.icon_student_gif = PhotoImage(file="student_icon.gif")
        self.icon_pro_gif = PhotoImage(file="pro_icon.gif")
        self.icon_mode_label = Label(self, cursor="hand1",
                                     background="#e1e1e1", relief="sunken")
        self.icon_mode_label.grid(row=0, column=2, padx=3, pady=3, 
                                      ipadx=3, ipady=3)
        self.icon_mode_tooltip = ToolTip(self.icon_mode_label,
                                         "Change Python mode  Alt-M", 2)

        # Save icon
        icon_save_gif = PhotoImage(file="save_icon.gif")
        self.icon_save_label = Label(self, image=icon_save_gif, 
                                     cursor="hand1", background="#e1e1e1", 
                                     relief="sunken")
        self.icon_save_label.image = icon_save_gif
        self.icon_save_label.grid(row=0, column=3, padx=3, pady=3, 
                                  ipadx=3, ipady=3)
        self.icon_save_tooltip = ToolTip(self.icon_save_label,
                                         "Save file  Ctrl-S", 3)

        # Open icon
        icon_open_gif = PhotoImage(file="open_icon.gif")
        self.icon_open_label = Label(self, image=icon_open_gif, 
                                     cursor="hand1", background="#e1e1e1", 
                                     relief="sunken")
        self.icon_open_label.image = icon_open_gif
        self.icon_open_label.grid(row=0, column=4, padx=3, pady=3, 
                                  ipadx=3, ipady=3)
        self.icon_open_tooltip = ToolTip(self.icon_open_label,
                                         "Open file  Ctrl-O", 4)

        root.bind('<KeyPress-Shift_L>', self.show_tooltips)
        root.bind('<KeyRelease-Shift_L>', self.destroy_tooltips)
                                      
    def switch_icon_mode(self, mode):
        if mode == "student":
            self.icon_mode_label.config(image=self.icon_student_gif)
        elif mode == "full":
            self.icon_mode_label.config(image=self.icon_pro_gif)

    def show_tooltips(self, event=None):
        self.icon_new_file_tooltip.inside()
        self.icon_run_tooltip.inside()
        self.icon_mode_tooltip.inside()
        self.icon_save_tooltip.inside()
        self.icon_open_tooltip.inside()

    def destroy_tooltips(self, event=None):
        self.icon_new_file_tooltip.outside()
        self.icon_run_tooltip.outside()
        self.icon_mode_tooltip.outside()
        self.icon_save_tooltip.outside()
        self.icon_open_tooltip.outside()
        
