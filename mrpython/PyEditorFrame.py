#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 11:38:21 2019

@author: 3535008
"""

from PyEditor import PyEditor
from tkinter import *
from TextLineNumbers import TextLineNumbers

class PyEditorFrame(Frame):
    
    def __init__(self, parent, open=False, filename=None):
        Frame.__init__(self,parent)
        
        self.linenumbers = TextLineNumbers(self, width=5, height=1)
        self.editor = PyEditor(self, self.linenumbers,open, filename)
        self.linenumbers.attach(self.editor)

        self.linenumbers.pack(expand=True,side="left", fill="both")
        
        
        
        self.editor.pack(side="right", fill="both", expand=True)

        self.sy = Scrollbar(self)
        
        self.sy.pack(expand=False,side="right", fill="y")
        self.editor.pack(expand=True, fill='both')
        self.sy.config(command=self.editor.yview)
        
   
        self.editor['yscrollcommand'] = self.sy.set
        self.pack()
        
        self.linenumbers.redraw()
        
        
        #
    #Action deleger au pyEditor courrant
    #
    
    def get_line_widget(self):
        return self.nametowidget(self.linenumbers.get_line_widget())
    
    def isOpen(self):
        return self.editor.isOpen()
    
    def long_title(self):
        return self.editor.long_title()
    
    def get_file_name(self):
        return self.editor.get_file_name()
    
    def close(self,event):
        return self.editor.close(event)


    def get_editor(self):
        return self.editor
    
    #returns the notebook needed in PyEditor
    def get_notebook(self):
        return self.nametowidget(self.winfo_parent())
    
    def save(self,event=None):
        return self.editor.save(event)

    def save_as(self,event=None):
        return self.editor.save_as(event)

    def save_as_copy(self,event=None):
        return self.editor.save_a_copy(event)

    def undo_event(self,event=None):
        return self.editor.undo_event(event)

    def redo_event(self,event=None):
        return self.editor.redo_event(event)

    def cut_event(self,event=None):
        return self.editor.cut(event)

    def copy_event(self,event=None):
        return self.editor.copy(event)

    def paste_event(self,event=None):
        return self.editor.paste(event)

    def select_all_event(self,event=None):
        return self.editor.select_all(event)

    def find_event(self,event=None):
        return self.editor.find_event(event)

    def find_again_event(self, event=None):
        return self.editor.find_again_event(event)

    def find_selection_event(self, event=None):
        return self.editor.find_selection_event(event)

    def find_in_files_event(self, event=None):
       return self.editor.find_in_files_event(event)

    def replace_event(self, event=None):
         return self.editor.replace_event(event)

    def goto_line_event(self,event=None):
        return self.editor.goto_line_event(event)

    def indent_region_event(self,event=None):
        return self.editor.indent_region_event(event)

    def comment_region_event(self,event=None):
        return self.editor.comment_region_event(event)

    def dedent_region_event(self, event=None):
        return self.editor.dedent_region_event(event)

    def uncomment_region_event(self, event=None):
        return self.editor.uncomment_region_event(event)

    def tabify_region_event(self, event=None):
        return self.editor.tabify_region_event(event)

    def untabify_region_event(self, event=None):
        return self.editor.untabify_region_event(event)

    def toggle_tabs_event(self, event=None):
        return self.editor.toggle_tabs_event(event)


    def increase_font_size_event(self, event=None):
        return self.editor.increase_font_size_event(event)

    def decrease_font_size_event(self, event=None):
        return self.editor.decrease_font_size_event(event)
    
    

    def _asktabwidth(self):
        return self.editor._asktabwidth()

    def smart_backspace_event(self, event):
        return self.editor.smart_backspace_event(event)


    def newline_and_indent_event(self, event):
        return self.editor.newline_and_indent_event(event)
    def smart_indent_event(self, event):
        return self.editor.smart_indent_event(event)

    def set_notabs_indentwidth(self):
        return self.editor.set_notabs_indentwidth()

    def _build_char_in_string_func(self, startindex):
        return self.editor._build_char_in_string_func(startindex)

    def is_char_in_string(self, text_index):
        return self.editor.is_char_in_string(text_index)
    
    def reindent_to(self, column):
        return self.editor.reindent_to(column)

    def _make_blanks(self, n):
        return self.editor._make_blanks(n)

    def set_region(self, head, tail, chars, lines):
        return self.editor.set_region(head, tail, chars, lines)

    def get_region(self):
        return self.editor.get_region()
    
    