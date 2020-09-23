#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 14:03:21 2019

@author: 3535008
"""

try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk
from tincan import tracing_mrpython as tracing

class CloseableNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

        self.old_tab = ""
        self.new_tab = ""

    def get_filename(self, tab_path):
        try:
            return self.nametowidget(tab_path).get_file_name()
        except KeyError as path:
            error = "no widget with this path:{}".format(path)
            print(error)
            return error

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        self.old_tab = self.select()
        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        # Code for tracing changed tabs
        self.new_tab = self.select()
        if not self.instate(['pressed']) and self.old_tab != self.new_tab and self.old_tab != "":
            old_tab_filename = self.get_filename(self.old_tab)
            new_tab_filename = self.get_filename(self.new_tab)
            tracing.send_statement("switched", "file",
                                   {"https://www.lip6.fr/mocah/invalidURI/extensions/old-tab": old_tab_filename,
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/current-tab": new_tab_filename})

        # Code for closing tab
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        try:
            index = self.index("@%d,%d" % (event.x, event.y))
        except tk.TclError:
            return

        if "close" in element and self._active == index:
            old_tab_filename = self.get_filename(self.old_tab)
            #do the proper linking to the event
            self.close_current_editor()
                        self.new_tab = self.select()
            if self.new_tab != "":
                new_tab_filename = self.get_filename(self.new_tab)
            else:
                new_tab_filename = "no tab selected"
            tracing.send_statement("closed", "file",
                                   {"https://www.lip6.fr/mocah/invalidURI/extensions/closed-tab": old_tab_filename,
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/current-tab": new_tab_filename})
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None
        
    def close_current_editor(self,event=None):
        print("Should be overrided")

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                        })
                    ]
                })
            ]
        })
    ])