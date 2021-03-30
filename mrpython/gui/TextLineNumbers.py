import tkinter as tk

class TextLineNumbers(tk.Canvas):
    def __init__(self, min_width, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.min_width = min_width
        self.font = "Helvetica 12"

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            myText = self.create_text(2,y,anchor="nw", font = self.textwidget.font, text=linenum)
            
            bounds = self.bbox(myText)  # returns a tuple like (x1, y1, x2, y2)
            new_width = max(bounds[2]-bounds[0], self.min_width)
            self.configure(width=new_width)
            i = self.textwidget.index("%s+1line" % i)