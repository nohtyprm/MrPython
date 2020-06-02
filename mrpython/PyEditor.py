import os
import string
import platform
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
from tkinter.font import Font, nametofont

from tkinter import *
from configHandler import MrPythonConf
from Search import SearchDialog
from Search import GrepDialog
from Search import ReplaceDialog
import PyParse
import sys
import Bindings

from HighlightingText import HighlightingText
_py_version = ' (%s)' % platform.python_version()
from tincan import tracing_mrpython as tracing
import re


class Line:
    def __init__(self, line_number, instruction, type):
        self.line_number = line_number
        self.instruction = instruction
        self.type = type

    def __str__(self):
        return "line-number: " + str(self.line_number) + " instruction: '" + self.instruction + \
               "'  instruction-type: " + self.type


class PyEditor(HighlightingText):
    from IOBinding import  IOBinding, filesystemencoding, encoding
    from UndoDelegator import  UndoDelegator
    from Percolator import Percolator
    from ColorDelegator import  ColorDelegator

    def __init__(self, parent, linewidget, open=False, filename=None):

        HighlightingText.__init__(self,parent)

        
        self.list=parent.get_notebook()

        self.linewidget = linewidget

        self.recent_files_path = os.path.join(MrPythonConf.GetUserCfgDir(), 'recent-files.lst')

        self.apply_bindings()

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ''


        # usetabs true  -> literal tab characters are used by indent and
        #                  dedent cmds, possibly mixed with spaces if
        #                  indentwidth is not a multiple of tabwidth,
        #                  which will cause Tabnanny to nag!
        #         false -> tab characters are converted to spaces by indent
        #                  and dedent cmds, and ditto TAB keystrokes
        # Although use-spaces=0 can be configured manually in config-main.def,
        # configuration of tabs v. spaces is not supported in the configuration
        # dialog.  MRPYTHON promotes the preferred Python indentation: use spaces!
        usespaces = MrPythonConf.GetOption('main', 'Indent',
                                       'use-spaces', type='bool')
        self.usetabs = not usespaces
        
        # tabwidth is the display width of a literal tab character.
        # CAUTION:  telling Tk to use anything other than its default
        # tab setting causes it to use an entirely different tabbing algorithm,
        # treating tab stops as fixed distances from the left margin.
        # Nobody expects this, so for now tabwidth should never be changed.
        self.tabwidth = 8    # must remain 8 until Tk is fixed.

        # indentwidth is the number of screen characters per indent level.
        # The recommended Python indentation is four spaces.
        self.indentwidth = self.tabwidth
        self.set_notabs_indentwidth()
        
        # If context_use_ps1 is true, parsing searches back for a ps1 line;
        # else searches for a popular (if, def, ...) Python stmt.
        self.context_use_ps1 = False



        # When searching backwards for a reliable place to begin parsing,
        # first start num_context_lines[0] lines back, then
        # num_context_lines[1] lines back if that didn't work, and so on.
        # The last value should be huge (larger than the # of lines in a
        # conceivable file).
        # Making the initial values larger slows things down more often.
        self.num_context_lines = 50, 500, 5000000
        self.per = per = self.Percolator(self)
        self.undo = undo = self.UndoDelegator(self)
        per.insertfilter(undo)

        self.undo_block_start = undo.undo_block_start
        self.undo_block_stop = undo.undo_block_stop
        undo.set_saved_change_hook(self.saved_change_hook)

        self.io = io = self.IOBinding(self)
        io.set_filename_change_hook(self.filename_change_hook)
        
        self.color = None # initialized below in self.ResetColorizer

        self.good_load = False
        if open:
            if filename:
                if os.path.exists(filename) and not os.path.isdir(filename):
                    if io.loadfile(filename):
                        self.good_load = True
                        is_py_src = self.ispythonsource(filename)
                else:
                    io.set_filename(filename)
            else:
                self.good_load = self.io.open(editFile=filename)
        else:
            self.good_load=True

        self.ResetColorizer()
        self.saved_change_hook()
        self.askyesno = tkMessageBox.askyesno
        self.askinteger = tkSimpleDialog.askinteger

        # specific font
        self.font = nametofont(self.cget('font')).copy()
        self.configure(font=self.font)


        self.old_line = None

        # Used for tracing keywords. Check send_keyword for more information.
        self.typed_char = False # User previously typed a character


    def apply_bindings(self,keydefs=None):
        self.bind("<<smart-backspace>>",self.smart_backspace_event)
        self.bind("<<newline-and-indent>>",self.newline_and_indent_event)
        self.bind("<<smart-indent>>",self.smart_indent_event)

        self.bind('<KeyPress>', self.keypress_event)
        self.bind("<<paste>>", self.insert_event)
        self.bind("<<copy>>", self.copied_event)
        self.bind("<<prev-move-cursor>>", self.prev_move_cursor_event)
        self.bind("<<move-cursor>>", self.move_cursor_event)
        prev_move_cursor = ['<KeyPress-Left>', '<KeyPress-Right>', '<KeyPress-Up>', '<KeyPress-Down>',
                        '<ButtonPress-1>']
        move_cursor = ['<KeyRelease-Left>', '<KeyRelease-Right>', '<KeyRelease-Up>', '<KeyRelease-Down>',
                        '<ButtonRelease-1>']
        self.event_add("<<prev-move-cursor>>", *prev_move_cursor)
        self.event_add("<<move-cursor>>", *move_cursor)

        #bindings keys
        if keydefs is None:
            keydefs=Bindings.default_keydefs
        for event, keylist in keydefs.items():
            if keylist:
                self.event_add(event, *keylist)

    def ResetColorizer(self):
        "Update the color theme"
        # Called from self.filename_change_hook and from configDialog.py
        self._rmcolorizer()
        self._addcolorizer()
        theme = MrPythonConf.GetOption('main','Theme','name')
        normal_colors = MrPythonConf.GetHighlight(theme, 'normal')
        cursor_color = MrPythonConf.GetHighlight(theme, 'cursor', fgBg='fg')
        select_colors = MrPythonConf.GetHighlight(theme, 'hilite')
        self.config(
            foreground=normal_colors['foreground'],
            background=normal_colors['background'],
            insertbackground=cursor_color,
            selectforeground=select_colors['foreground'],
            selectbackground=select_colors['background'],
            )
    
    IDENTCHARS = string.ascii_letters + string.digits + "_"

    def colorize_syntax_error(self, text, pos):
        text.tag_add("ERROR", pos)
        char = text.get(pos)
        if char and char in self.IDENTCHARS:
            text.tag_add("ERROR", pos + " wordstart", pos)
        if '\n' == text.get(pos):   # error at line end
            text.mark_set("insert", pos)
        else:
            text.mark_set("insert", pos + "+1c")
        text.see(pos)
        
    def _rmcolorizer(self):
        if not self.color:
            return
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = None
        
    def _addcolorizer(self):
        if self.color:
            return
        if self.ispythonsource(self.io.filename):
            self.color = self.ColorDelegator()
        if self.color:
            self.per.removefilter(self.undo)
            self.per.insertfilter(self.color)
            self.per.insertfilter(self.undo)

    def get_file_name(self):
        return self.short_title()

    def saved_change_hook(self):
        short = self.short_title()
        long = self.long_title()
        if short and long:
            title = short + " - " + long + _py_version
        elif short:
            title = short
        elif long:
            title = long
        else:
            title = "Untitled"
        icon = short or long or title
        if not self.get_saved():
            title = "*%s*" % title
            icon = "*%s" % icon

    def short_title(self):
        filename = self.io.filename
        if filename:
            filename = os.path.basename(filename)
        else:
            filename = "Sans nom"
        # return unicode string to display non-ASCII chars correctly
        return self._filename_to_unicode(filename)

    def _filename_to_unicode(self, filename):
        """convert filename to unicode in order to display it in Tk"""
        if isinstance(filename, str) or not filename:
            return filename
        else:
            try:
                return filename.decode(self.filesystemencoding)
            except UnicodeDecodeError:
                # XXX
                try:
                    return filename.decode(self.encoding)
                except UnicodeDecodeError:
                    # byte-to-byte conversion
                    return filename.decode('iso8859-1')

    def long_title(self):
        # return unicode string to display non-ASCII chars correctly
        return self._filename_to_unicode(self.io.filename or "")

    def get_saved(self):
        return self.undo.get_saved()

    def set_saved(self, flag):
        self.undo.set_saved(flag)

    def reset_undo(self):
        self.undo.reset_undo()

    def open(self, filename, action=None):
        ##dans IOBindings?
        assert filename
        filename = self.canonize(filename)
        if os.path.isdir(filename):
            # This can happen when bad filename is passed on command line:
            tkMessageBox.showerror(
                "File Error",
                "%r is a directory." % (filename,),
                master=self)
                #master=self.root)
            return None
        key = os.path.normcase(filename)
        
        if action:
            # Don't create window, perform 'action', e.g. open in same window
            return action(filename)
        
    def canonize(self, filename):
        if not os.path.isabs(filename):
            try:
                pwd = os.getcwd()
            except OSError:
                pass
            else:
                filename = os.path.join(pwd, filename)
        return os.path.normpath(filename)

    def isOpen(self):
        return self.good_load

    def filename_change_hook(self):
        if self.list:
            self.list.changerFileName(self)

    def maybesave(self):
        if self.io:
            return self.io.maybesave()

    def maybesave_run(self):
        if self.io:
            return self.io.maybesave_run()

    def _close(self):
        #WindowList.unregister_callback(self.postwindowsmenu)
        #self.unload_extensions()
        self.io.close()
        self.io = None
        self.undo = None
        self.tkinter_vars = None
        self.per.close()
        self.per = None

    def update_recent_files_list(self, new_file=None):
        self.list.add_recent_file(new_file)


    def ispythonsource(self, filename):
        if not filename or os.path.isdir(filename):
            return True
        base, ext = os.path.splitext(os.path.basename(filename))
        if os.path.normcase(ext) in (".py", ".pyw"):
            return True
        line = self.get('1.0', '1.0 lineend')
        return line.startswith('#!') and 'python' in line

    #
    # Menu Actions
    #

    def close(self,event):
        reply = self.maybesave()
        if str(reply) != "cancel":
            self._close()
        return reply

    def save(self,event):
        return self.io.save(event)

    def save_as(self,event):
        return self.io.save_as(event)

    def save_as_copy(self,event):
        return self.io.save_a_copy(event)

    def undo_event(self,event):
        return self.undo.undo_event(event)

    def redo_event(self,event):
        return self.undo.redo_event(event)

    def cut(self,event):
        self.event_generate("<<Cut>>")
        return "break"

    def copy(self,event):
        if not self.tag_ranges("sel"):
            # There is no selection, so do nothing and maybe interrupt.
            return
        self.event_generate("<<Copy>>")
        return "break"

    def paste(self,event):
        self.event_generate("<<Paste>>")
        self.see("insert")
        return "break"

    def select_all(self, event):
        self.tag_add("sel", "1.0", "end-1c")
        self.mark_set("insert", "1.0")
        self.see("insert")
        return "break"

    def find_event(self, event):
        SearchDialog.find(self)
        return "break"

    def find_again_event(self, event):
        SearchDialog.find_again(self)
        return "break"

    def find_selection_event(self, event):
        SearchDialog.find_selection(self)
        return "break"

    def find_in_files_event(self, event):
        GrepDialog.grep(self, self.io, self.flist)
        return "break"

    def replace_event(self, event):
        ReplaceDialog.replace(self)
        return "break"

    def goto_line_event(self, event):
        lineno = tkSimpleDialog.askinteger("Goto",
                "Go to line number:",parent=self)
        if lineno is None:
            return "break"
        if lineno <= 0:
            self.bell()
            return "break"
        self.mark_set("insert", "%d.0" % lineno)
        self.see("insert")

    def comment_region_event(self,event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines) - 1):
            line = lines[pos]
            lines[pos] = '##' + line
        self.set_region(head, tail, chars, lines)


    def change_font_size(self, console, change_fun):
        
        fsize = self.font.cget('size')
        new_size = change_fun(fsize)
        if(new_size <= 0):
            new_size = 2 
        self.font.configure(size=new_size)
        console.change_font(self.font)
        self.event_generate("<<Change>>", when="tail")
        #edit.configure(font=font)
        
    

    #
    # Event propre au pyEditor
    #

    # If a selection is defined in the text widget, return (start,
    # end) as Tkinter text indices, otherwise return (None, None)
    def get_selection_indices(self):
        first = self.index("sel.first")
        last = self.index("sel.last")
        #weird bug..
        if first=="None" and last=="None":
            return None, None
        return first, last


    def indent_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = effective + self.indentwidth
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        return "break"
        
    def dedent_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = max(effective - self.indentwidth, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        return "break"
        
    def uncomment_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if not line:
                continue
            if line[:2] == '##':
                line = line[2:]
            elif line[:1] == '#':
                line = line[1:]
            lines[pos] = line
        self.set_region(head, tail, chars, lines)

    def tabify_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        if tabwidth is None: return
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, tabwidth)
                ntabs, nspaces = divmod(effective, tabwidth)
                lines[pos] = '\t' * ntabs + ' ' * nspaces + line[raw:]
        self.set_region(head, tail, chars, lines)

    def untabify_region_event(self, event):
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        if tabwidth is None: return
        for pos in range(len(lines)):
            lines[pos] = lines[pos].expandtabs(tabwidth)
        self.set_region(head, tail, chars, lines)

    def toggle_tabs_event(self, event):
        if self.askyesno(
              "Toggle tabs",
              "Turn tabs " + ("on", "off")[self.usetabs] +
              "?\nIndent width " +
              ("will be", "remains at")[self.usetabs] + " 8." +
              "\n Note: a tab is always 8 columns",
              parent=self):
            self.usetabs = not self.usetabs
            # Try to prevent inconsistent indentation.
            # User must change indent width manually after using tabs.
            self.indentwidth = 8
        return "break"
        
    def goto_line_event(self, event):
        lineno = tkSimpleDialog.askinteger("Goto",
                "Go to line number:",parent=self)
        if lineno is None:
            return "break"
        if lineno <= 0:
            self.bell()
            return "break"
        self.mark_set("insert", "%d.0" % lineno)
        self.see("insert")

    def _asktabwidth(self):
        return self.askinteger(
            "Tab width",
            "Columns per tab? (2-16)",
            parent=self,
            initialvalue=self.indentwidth,
            minvalue=2,
            maxvalue=16)

    def smart_backspace_event(self, event):
        tracing.user_is_typing()
        self.typed_char = False
        first, last = self.get_selection_indices()
        if first and last:
            self.send_deletion(first, last)
            if self.is_multi_line_deletion(first, last):
                self.reset_line()
            self.delete(first, last)
            self.mark_set("insert", first)
            return "break"
        # Delete whitespace left, until hitting a real char or closest
        # preceding virtual tab stop.
        chars = self.get("insert linestart", "insert")
        if chars == '':
            if self.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                self.delete("insert-1c")
                self.send_update_changed_line()
            else:
                self.bell()     # at start of buffer
            return "break"
        if  chars[-1] not in " \t":
            # easy: delete preceding real char
            self.delete("insert-1c")
            return "break"
        # Ick.  It may require *inserting* spaces if we back up over a
        # tab character!  This is written to be clear, not fast.
        tabwidth = self.tabwidth
        have = len(chars.expandtabs(tabwidth))
        assert have > 0
        want = ((have - 1) // self.indentwidth) * self.indentwidth
        # Debug prompt is multilined....
        if self.context_use_ps1:
            last_line_of_prompt = sys.ps1.split('\n')[-1]
        else:
            last_line_of_prompt = ''
        ncharsdeleted = 0
        while 1:
            if chars == last_line_of_prompt:
                break
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(tabwidth))
            if have <= want or chars[-1] not in " \t":
                break
        self.undo_block_start()
        self.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            self.insert("insert", ' ' * (want - have))
        self.undo_block_stop()
        return "break"


    def newline_and_indent_event(self, event):
        tracing.user_is_typing()
        # Trace last word if it's a keyword
        if self.typed_char:
            cursor = self.index("insert")
            self.send_keyword(cursor)
            self.typed_char = False

        first, last = self.get_selection_indices()
        self.undo_block_start()
        try:
            if first and last:
                self.send_deletion(first, last)
                if self.is_multi_line_deletion(first, last):
                    self.reset_line()
                self.delete(first, last)
                self.mark_set("insert", first)
            line = self.get("insert linestart", "insert")
            i, n = 0, len(line)
            while i < n and line[i] in " \t":
                i = i+1
            if i == n:
                # the cursor is in or at leading indentation in a continuation
                # line; just inject an empty line at the start
                self.insert("insert linestart", '\n')
                return "break"
            indent = line[:i]
            # strip whitespace before insert point unless it's in the prompt
            i = 0
            last_line_of_prompt = sys.ps1.split('\n')[-1]
            while line and line[-1] in " \t" and line != last_line_of_prompt:
                line = line[:-1]
                i = i+1
            if i:
                self.delete("insert - %d chars" % i, "insert")
            # strip whitespace after insert point
            while self.get("insert") in " \t":
                self.delete("insert")
            # start new line
            self.insert("insert", '\n')

            # adjust indentation for continuations and block
            # open/close first need to find the last stmt
            lno = index2line(self.index('insert'))
            y = PyParse.Parser(self.indentwidth, self.tabwidth)
            if not self.context_use_ps1:
                for context in self.num_context_lines:
                    startat = max(lno - context, 1)
                    startatindex = repr(startat) + ".0"
                    rawtext = self.get(startatindex, "insert")
                    y.set_str(rawtext)
                    bod = y.find_good_parse_start(
                              self.context_use_ps1,
                              self._build_char_in_string_func(startatindex))
                    if bod is not None or startat == 1:
                        break
                y.set_lo(bod or 0)
            else:
                r = self.tag_prevrange("console", "insert")
                if r:
                    startatindex = r[1]
                else:
                    startatindex = "1.0"
                rawtext = self.get(startatindex, "insert")
                y.set_str(rawtext)
                y.set_lo(0)

            c = y.get_continuation_type()
            if c != PyParse.C_NONE:
                # The current stmt hasn't ended yet.
                if c == PyParse.C_STRING_FIRST_LINE:
                    # after the first line of a string; do not indent at all
                    pass
                elif c == PyParse.C_STRING_NEXT_LINES:
                    # inside a string which started before this line;
                    # just mimic the current indent
                    self.insert("insert", indent)
                elif c == PyParse.C_BRACKET:
                    # line up with the first (if any) element of the
                    # last open bracket structure; else indent one
                    # level beyond the indent of the line with the
                    # last open bracket
                    self.reindent_to(y.compute_bracket_indent())
                elif c == PyParse.C_BACKSLASH:
                    # if more than one line in this stmt already, just
                    # mimic the current indent; else if initial line
                    # has a start on an assignment stmt, indent to
                    # beyond leftmost =; else to beyond first chunk of
                    # non-whitespace on initial line
                    if y.get_num_lines_in_stmt() > 1:
                        self.insert("insert", indent)
                    else:
                        self.reindent_to(y.compute_backslash_indent())
                else:
                    assert 0, "bogus continuation type %r" % (c,)
                return "break"

            # This line starts a brand new stmt; indent relative to
            # indentation of initial line of closest preceding
            # interesting stmt.
            indent = y.get_base_indent_string()
            self.insert("insert", indent)
            if y.is_block_opener():
                self.smart_indent_event(event)
            elif indent and y.is_block_closer():
                self.smart_backspace_event(event)
            return "break"
        finally:
            self.see("insert")
            self.undo_block_stop()
            self.send_update_changed_line(newline=True)

    def smart_indent_event(self, event):
        tracing.user_is_typing()
        first, last = self.get_selection_indices()
        self.undo_block_start()
        try:
            if first and last:
                if index2line(first) != index2line(last):
                    return self.indent_region_event(event)
                self.send_deletion(first, last)
                if self.is_multi_line_deletion(first, last):
                    self.reset_line()
                self.delete(first, last)
                self.mark_set("insert", first)
            prefix = self.get("insert linestart", "insert")
            raw, effective = classifyws(prefix, self.tabwidth)
            if raw == len(prefix):
                # only whitespace to the left
                self.reindent_to(effective + self.indentwidth)
            else:
                # tab to the next 'stop' within or to right of line's self:
                if self.usetabs:
                    pad = '\t'
                else:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                self.insert("insert", pad)
            self.see("insert")
            return "break"
        finally:
            self.undo_block_stop()


    def set_notabs_indentwidth(self):
        "Update the indentwidth if changed and not using tabs in this window"
        # Called from configDialog.py
        if not self.usetabs:
            self.indentwidth = MrPythonConf.GetOption('main', 'Indent','num-spaces',
                                                  type='int')

    # Our editwin provides a is_char_in_string function that works
    # with a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function for PyParse that accepts an
    # offset.

    def _build_char_in_string_func(self, startindex):
        def inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            return _icis(_startindex + "+%dc" % offset)
        return inner

    def is_char_in_string(self, text_index):
        if self.color:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, or the character is tagged as being in a string
            return self.tag_prevrange("TODO", text_index) or \
                   "STRING" in self.tag_names(text_index)
        else:
            # The colorizer is missing: assume the worst
            return 1

    # Delete from beginning of line to insert point, then reinsert
    # column logical (meaning use tabs if appropriate) spaces.

    def reindent_to(self, column):
        self.undo_block_start()
        if self.compare("insert linestart", "!=", "insert"):
            self.delete("insert linestart", "insert")
        if column:
            self.insert("insert", self._make_blanks(column))
        self.undo_block_stop()

     # Make string that displays as n leading blanks.

    def _make_blanks(self, n):
        if self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return '\t' * ntabs + ' ' * nspaces
        else:
            return ' ' * n

    def set_region(self, head, tail, chars, lines):
        newchars = "\n".join(lines)
        if newchars == chars:
            self.bell()
            return
        self.tag_remove("sel", "1.0", "end")
        self.mark_set("insert", head)
        self.undo_block_start()
        self.delete(head, tail)
        self.insert(head, newchars)
        self.undo_block_stop()
        self.tag_add("sel", head, "insert")

    def get_region(self):
        first, last = self.get_selection_indices()
        if first and last:
            head = self.index(first + " linestart")
            tail = self.index(last + "-1c lineend +1c")
        else:
            head = self.index("insert linestart")
            tail = self.index("insert lineend +1c")
        chars = self.get(head, tail)
        lines = chars.split("\n")
        return head, tail, chars, lines

    #
    # Functions and events used for tracing
    #
    def get_current_line_number(self):
        """Get the line number of the cursor"""
        cursor = self.index("insert")
        line = cursor.split('.')[0]
        return int(line)

    def get_current_instruction(self):
        return self.get("insert linestart", "insert lineend")

    def get_instruction(self, line_number):
        return self.get(str(line_number) + ".0 linestart", str(line_number) + ".0 lineend")

    def get_number_of_lines(self):
        end = self.index("end-1c")
        line = end.split('.')[0]
        return int(line)

    def is_multi_line_deletion(self, first, last):
        return first.split('.')[0] != last.split('.')[0]

    def maybe_get_function_name(self, line_number):
        function_name = ""
        if line_number < 1:
            return function_name
        instruction = self.get_instruction(line_number)
        instruction = instruction.strip()
        if instruction.startswith("def "):  # Check the first previous line starting with "def "
            instruction = instruction[4:]
            function_name = instruction.split('(')[0]
            function_name = function_name.strip()
            return function_name
        return function_name

    def get_previous_function(self, line_number):
        """Get the name of the previous function defined"""
        while line_number >= 1:
            function_name = self.maybe_get_function_name(line_number)
            if function_name:
                return function_name
            line_number -= 1
        return "no function defined"

    def is_under_signature(self, line_number):
        while line_number > 1:
            instruction = self.get_instruction(line_number)
            if "'''" in instruction or '"""' in instruction:
                if self.maybe_get_function_name(line_number-1) != "":
                    return True
                break
            elif "STRING" not in self.tag_names(str(line_number)+".0"):
                break
            line_number -= 1
        return False

    def is_part_of_multistring(self, line_number):
        beginning_index = str(line_number) + ".0"
        beginning_tags = self.tag_names(beginning_index)
        beginning_char = self.get(beginning_index)
        if "STRING" in beginning_tags and beginning_char != "'" and beginning_char != '"':
            return True
        return False

    def is_one_liner_signature(self, instruction):
        pattern = re.compile(r'("""|\'\'\').*("""|\'\'\')')
        return pattern.search(instruction) is not None

    def is_comment_maybe_type_declaration(self, comment):
        pattern = re.compile(r'\w+\s*:.*')
        return pattern.search(comment) is not None

    def is_comment_exercise_declaration(self, comment):
        pattern = re.compile(r'ex\D*(\d+)\D+(\d+)', re.IGNORECASE)
        return pattern.search(comment) is not None

    def create_line(self, line_number):
        line_instruction = self.get_instruction(line_number)
        if "'''" in line_instruction or '"""' in line_instruction:
            if self.is_one_liner_signature(line_instruction):
                line_type = "signature-oneliner"
            elif self.maybe_get_function_name(line_number-1) != "":
                line_type = "signature-begining"
            elif self.is_under_signature(line_number-1):
                line_type = "signature-ending"
            else:
                line_type = "multi-string"
        elif self.is_part_of_multistring(line_number):
            if self.is_under_signature(line_number-1):
                line_type = "signature-middle"
            else:
                line_type = "multi-string"
        else:
            instruction_comment = line_instruction.split("#", 1)
            comment_tags = self.tag_nextrange("COMMENT", str(line_number) + ".0 linestart",
                                              str(line_number) + ".0 lineend")
            if len(instruction_comment) >= 2 and len(comment_tags) != 0:
                instruction, comment = instruction_comment[0].strip(), instruction_comment[1].strip()
            else:
                instruction, comment = instruction_comment[0].strip(), ""
            if instruction and comment:
                line_type = "instruction_and_comment"
            elif instruction:
                line_type = "instruction"
            elif comment:
                if self.is_comment_maybe_type_declaration(comment):
                    line_type = "comment-maybe-type"
                elif self.is_comment_exercise_declaration(comment):
                    line_type = "comment-exercise"
                else:
                    line_type = "comment"
            else:
                line_type = "empty"
        line = Line(line_number, line_instruction, line_type)
        return line

    def create_changed_line_extensions(self, old_line, new_line):
        extensions = {"https://www.lip6.fr/mocah/invalidURI/extensions/line-number": old_line.line_number,
                      "https://www.lip6.fr/mocah/invalidURI/extensions/old-instruction-type": old_line.type,
                      "https://www.lip6.fr/mocah/invalidURI/extensions/old-instruction": old_line.instruction,
                      "https://www.lip6.fr/mocah/invalidURI/extensions/new-instruction-type": new_line.type,
                      "https://www.lip6.fr/mocah/invalidURI/extensions/new-instruction": new_line.instruction}
        return extensions

    def send_update_changed_line(self, newline = False):
        if self.old_line is None:
            return
        old_line = self.old_line
        new_line = self.create_line(old_line.line_number)
        cursor_line_number = self.get_current_line_number()
        cursor_changed_line = old_line.line_number != cursor_line_number
        not_both_empty = (old_line.instruction != "" and not old_line.instruction.isspace())
        not_both_empty = not_both_empty or (new_line.instruction != "" and not new_line.instruction.isspace())
        instruction_has_been_modified = old_line.instruction.strip() != new_line.instruction.strip()
        if newline or cursor_changed_line:
            if not_both_empty and instruction_has_been_modified:
                if new_line.line_number == 1:
                    tracing.check_modified_student_number(new_line.instruction)
                extensions = self.create_changed_line_extensions(old_line,new_line)
                tracing.send_statement("modified", "line", extensions)
            self.old_line = self.create_line(cursor_line_number)

    def reset_line(self):
        self.old_line = None

    def send_keyword(self, end_word):
        """We send a keyword when the tag 'KEYWORD' is in the tags of end_word.
        end_word : the character of the last word

        This function is called when self.typed_char is True and:
        -a user types a non alphanum character (keypress_event). end_word is the character of the last word.
        -a user types a newline (newline_and_indent_event).
        end_word is the character of the previous instruction's last character.
        -the cursor has been moved (prev_move_cursor_event and move_cursor_event)
        end_word is the character of the previous cursor position.

        We don't simply check all keypress because we want to prevent cases where the user types something
        like 'define' or 'assert'.
        In these cases, the user typed the keywords 'def' or 'as' but we don't want to trace these.

        self.typed_char is used to prevent sending the same keyword multiple times and
        to only trace the keywords the user effectively typed.
        """
        if end_word == "1.0":  # Bug with select all
            return
        tags = self.tag_names(end_word)
        if 'KEYWORD' in self.tag_names(end_word + "-1c"):
            index1, index2 = self.tag_prevrange('KEYWORD', end_word)
            keyword = self.get(index1, index2)
            line_number = self.index("insert").split(".")[0]
            tracing.send_statement("typed", "keyword",
                                   {"https://www.lip6.fr/mocah/invalidURI/extensions/keyword-typed": keyword,
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/filename": self.short_title(),
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/line-number": line_number
                                    })
            # print("Keyword typed: " + keyword)

    def send_deletion(self, first, last):
        tracing.send_statement("deleted", "text",
                               {"https://www.lip6.fr/mocah/invalidURI/extensions/text": self.get(first, last),
                                "https://www.lip6.fr/mocah/invalidURI/extensions/first-index": first,
                                "https://www.lip6.fr/mocah/invalidURI/extensions/last-index": last,
                                "https://www.lip6.fr/mocah/invalidURI/extensions/filename": self.short_title()})

    def prev_move_cursor_event(self, event):
        if self.typed_char:
            self.send_keyword(self.index("insert"))
            self.typed_char = False

    def move_cursor_event(self, event):
        self.send_update_changed_line()

    def insert_event(self, event):
        pasted_text = self.clipboard_get()
        if pasted_text != "":
            tracing.send_statement("inserted", "text",
                                   {"https://www.lip6.fr/mocah/invalidURI/extensions/text": self.clipboard_get(),
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/index": self.index("insert"),
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/filename": self.short_title()})

    def copied_event(self, event):
        first, last = self.get_selection_indices()
        if first and last:
            text = self.get(first, last)
            tracing.send_statement("copied", "text",
                                   {"https://www.lip6.fr/mocah/invalidURI/extensions/text": text,
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/filename": self.short_title(),
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/first-index": first,
                                    "https://www.lip6.fr/mocah/invalidURI/extensions/last-index": last,
                                    })

    def keypress_event(self, event):
        tracing.user_is_typing()

        keypress_is_char = len(event.char) == 1
        keypress_is_separator = keypress_is_char and event.char.isalnum() is False
        if self.typed_char and (keypress_is_separator or event.keysym == "space"):
            self.send_keyword(self.index("insert"))

        if not self.typed_char:
            self.typed_char = keypress_is_char

        if self.old_line is None:
            self.old_line = self.create_line(self.get_current_line_number())


# "line.col" -> line, as an int
def index2line(index):
    return int(float(index))

def classifyws(s, tabwidth):
    raw = effective = 0
    for ch in s:
        if ch == ' ':
            raw = raw + 1
            effective = effective + 1
        elif ch == '\t':
            raw = raw + 1
            effective = (effective // tabwidth + 1) * tabwidth
        else:
            break
    return raw, effective











