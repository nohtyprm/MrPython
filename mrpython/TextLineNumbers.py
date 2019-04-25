#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 12:38:00 2019

@author: 3535008
"""

import tkinter as tk

class TextLineNumbers(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.font = "Helvetica 12"

    def attach(self, text_widget):
        self.textwidget = text_widget
    
    def configure(self, font="Helvetica 12"):
        self.font = font
    
    def get_line_widget(self):
        return self
    """
    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,font=self.font,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)
        self.after(30, self.redraw)
    """
    def redraw(self, *args):
        self.delete(1.0, tk.END)
        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            """
            Not a good solution... it seemed to work fine with a canvas in handling a text line fulfilling more 
            than one line but not for text
            Yet canvas gave other zooming problems...
            """
            nb_char_per_line = int(self.textwidget.winfo_width()/self.textwidget.font.measure("0") - 0.4)
            j = self.textwidget.index("%s lineend" %i)
            #compute number of \n to add to string
            colnum = int(str(j).split(".")[1])
            #at initialization, nb_char_per_line seems to be 0... Seems legit
            if(nb_char_per_line > 0):
                for k in range(0, colnum//nb_char_per_line):
                    linenum+='\n'
            self.insert(tk.INSERT, linenum+'\n')
            i = self.textwidget.index("%s+1line" % i)
        self.after(30, self.redraw)