# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 22:00:00 2019

@author: Matthieu
"""
import tkinter as tk


#proxy causes "sel" tag not being added, it appears to be a windows problem
#see the link which seems to point out the same issue
#https://stackoverflow.com/questions/47184080/how-do-i-track-whether-a-tkinter-text-widget-has-been-modified-using-a-proxy-tha
class HighlightingText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "__orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.tag_configure("match", background="white", foreground="black")
        self.tag_configure("nomatch", background="red", foreground="black")
        self.matched = False
        self.nomatch_lpar = False
        self.nomatch_rpar = False
        self.index_r_par = 0
        self.index_l_par = 0
    
    def remove_tags(self, tag, tagnomatch):
        #remove previous tags
        if self.matched:
            self.tag_remove(tag, self.index_r_par)
            self.tag_remove(tag, self.index_l_par)
        elif self.nomatch_lpar:
            self.tag_remove(tagnomatch, self.index_r_par)
        elif self.nomatch_rpar:
            self.tag_remove(tagnomatch, self.index_l_par)
        self.matched = False
        self.nomatch_lpar = False
        self.nomatch_rpar = False
    
    def highlight_pattern(self, tag, tagnomatch, opening_token, closing_token, start=tk.CURRENT + " linestart", end=tk.CURRENT + " lineend",
                          regexp=False):

            
        start = self.index(start)
        end = self.index(end)
        current = self.index("insert")
        #print("start vaut " + str(start), " end vaut " + str(end), " current vaut " + str(current))
        nb_left_par = 0
        nb_right_par = 0
        
        (line_nb, end_pos) = map(lambda c: int(c), current.split('.'))
        end_pos -= 1
        c = self.get(str(line_nb) + "." + str(end_pos))
        #print("c vaut " + str(c))

        i = 1
        #starting from left to right
        if c == closing_token:
            nb_right_par = 1
            #slicing notation for reversing list
            line_text = self.get(start, current) [::-1]
            for c in line_text[1:]:
                if c == opening_token:
                    nb_left_par = nb_left_par + 1
                    if nb_left_par == nb_right_par:
                        self.matched = True
                        break
                if c == closing_token:
                    nb_right_par = nb_right_par + 1
                i = i+1
            
            self.index_r_par = str(line_nb) + "." + str(end_pos)
            if self.matched:
                self.index_l_par =  str(line_nb) + "." + str(end_pos -i)
                self.tag_add(tag, self.index_r_par)
                self.tag_add(tag, self.index_l_par)
                #print("lindex de la parenthese est " + str(self.index_l_par) + " " +str(self.index_r_par))
            else:
                self.tag_add(tagnomatch, self.index_r_par)
                self.nomatch_lpar = True
        
        elif c == opening_token:
            nb_left_par = 1
            
            line_text = self.get(current, end)
            for c in line_text:
                if c == closing_token:
                    nb_right_par = nb_right_par + 1
                    if nb_left_par == nb_right_par:
                        self.matched = True
                        break
                if c == opening_token:
                    nb_left_par += 1
                i += 1
            self.index_l_par = str(line_nb) + "." + str(end_pos)
            if self.matched:
                self.index_r_par = str(line_nb) + "." + str(end_pos+i)
                self.tag_add(tag, self.index_l_par)
                self.tag_add(tag, self.index_r_par)
            else:
                self.tag_add(tagnomatch, self.index_l_par)
                self.nomatch_rpar = True
        else:
            return False
        return True
    """
    for more info on proxy:
    https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
    cf. Brian Oakley answer
    """
    def _proxy(self, *args):
        cmd = (self._orig,) + args
        result = None
        try:
            result = self.tk.call(cmd)
        except Exception:
            result = None
        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "delete") or 
            args[0:3] == ("mark", "set", "insert")):
            self.remove_tags("match", "nomatch")
            self.highlight_pattern("match", "nomatch", "(", ")") or self.highlight_pattern("match", "nomatch", "[", "]") or self.highlight_pattern("match", "nomatch", "{", "}")
            
        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")
            
        if result == None:
            return None
        return result        