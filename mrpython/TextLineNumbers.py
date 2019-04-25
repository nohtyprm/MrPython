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

    def redraw(self, *args):
        self.delete(1.0, tk.END)
        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            linenum = str(i).split(".")[0]
            self.insert(tk.INSERT, linenum+'\n')
            i = self.textwidget.index("%s+1line" % i)
        #maybe use the proxy and not the redraw method
        self.after(30, self.redraw)