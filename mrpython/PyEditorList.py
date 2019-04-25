import os
from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font, nametofont
import tkinter.messagebox as tkMessageBox
from PyEditorFrame import PyEditorFrame

from CloseableNotebook import CloseableNotebook

MODULE_PATH = os.path.dirname(__file__)

def expand_filename(fname):
    return MODULE_PATH + "/" + fname

class PyEditorList(CloseableNotebook):
    """
    Manages the PyEditor widgets, in editor interface
    """
    def __init__(self,parent):
        from configHandler import MrPythonConf
        CloseableNotebook.__init__(self, parent)#), height=500)
        self.parent = parent
        self.sizetab = 0
        self.recent_files_menu = None

        self.recent_files_path = os.path.join(MrPythonConf.GetUserCfgDir(),
                                              'recent-files.lst')

    def get_size(self):
        return self.sizetab

    def add(self, child, editor_widget, **kw):
        super(PyEditorList, self).add(child, **kw)
        child.list = self
        self.select(child)
        self.sizetab += 1

    def changerFileName(self,editor):
        if editor.isOpen():
            self.tab(editor,text=editor.get_file_name())

    def get_current_editor(self):
        return self.nametowidget((self.nametowidget(self.select())).get_editor())

    def add_recent_file(self,new_file=None):
        "Load and update the recent files list and menus"
        rf_list = []
        if os.path.exists(self.recent_files_path):
            with open(self.recent_files_path, 'r',
                      encoding='utf_8', errors='replace') as rf_list_file:
                rf_list = rf_list_file.readlines()
        if new_file:
            new_file = os.path.abspath(new_file) + '\n'
            if new_file in rf_list:
                rf_list.remove(new_file)  # move to top
            rf_list.insert(0, new_file)
        # clean and save the recent files list
        bad_paths = []
        for path in rf_list:
            if '\0' in path or not os.path.exists(path[0:-1]):
                bad_paths.append(path)
        rf_list = [path for path in rf_list if path not in bad_paths]
        ulchars = "1234567890ABCDEFGHIJK"
        rf_list = rf_list[0:len(ulchars)]
        try:
            with open(self.recent_files_path, 'w',
                        encoding='utf_8', errors='replace') as rf_file:
                rf_file.writelines(rf_list)
        except OSError as err:
            if not getattr(self, "recentfilelist_error_displayed", False):
                self.recentfilelist_error_displayed = True
                tkMessageBox.showerror(title='MrPython Error',
                    message='Unable to update Recent Files list:\n%s'
                        % str(err),
                    parent=self)

        menu=self.recent_files_menu
        if menu:
            menu.delete(0, END)  # clear, and rebuild:
            for i, file_name in enumerate(rf_list):
                file_name = file_name.rstrip()  # zap \n
                # make unicode string to display non-ASCII chars correctly
                ufile_name = self._filename_to_unicode(file_name)
                callback = self.__recent_file_callback(file_name)
                menu.add_command(label=ulchars[i] + " " + ufile_name,command=callback,underline=0)

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

    def __recent_file_callback(self, file_name):
        def open_recent_file(fn_closure=file_name):

            if(self.focusOn(fn_closure)==False):
                fileEditor=PyEditorFrame(self,open=True,filename=fn_closure)
                if(fileEditor.isOpen()):
                    self.add(fileEditor,text=fileEditor.get_file_name())
        return open_recent_file

    def set_recent_files_menu(self,menu):
        self.recent_files_menu=menu
        self.add_recent_file()

    def focusOn(self,long_filename):
        for wn in self.tabs():
            widget=self.nametowidget(wn)
            if(widget.long_title()==long_filename):
                self.select(widget)
                return True
        return False

    def get_current_frame(self):
        return self.nametowidget(self.select())
    #
    #Action deleger au pyEditor courrant
    #
    def close_current_editor(self,event=None):
        reply=self.get_current_frame().get_editor().close(event)
        if reply!="cancel":
            self.sizetab-=1
            self.forget(self.get_current_frame())
        return reply


    def save(self,event=None):
        if self.get_size() > 0:
            return self.get_current_editor().save(event)
        else:
            return None

    def save_as(self,event=None):
        return self.get_current_editor().save_as(event)

    def save_as_copy(self,event=None):
        return self.get_current_editor().save_a_copy(event)

    def undo_event(self,event=None):
        return self.get_current_editor().undo_event(event)

    def redo_event(self,event=None):
        return self.get_current_editor().redo_event(event)

    def cut_event(self,event=None):
        return self.get_current_editor().cut(event)

    def copy_event(self,event=None):
        return self.get_current_editor().copy(event)

    def paste_event(self,event=None):
        return self.get_current_editor().paste(event)

    def select_all_event(self,event=None):
        return self.get_current_editor().select_all(event)

    def find_event(self,event=None):
        return self.get_current_editor().find_event(event)

    def find_again_event(self, event=None):
        return self.get_current_editor().find_again_event(event)

    def find_selection_event(self, event=None):
        return self.get_current_editor().find_selection_event(event)

    def find_in_files_event(self, event=None):
       return self.get_current_editor().find_in_files_event(event)

    def replace_event(self, event=None):
         return self.get_current_editor().replace_event(event)

    def goto_line_event(self,event=None):
        return self.get_current_editor().goto_line_event(event)

    def indent_region_event(self,event=None):
        return self.get_current_editor().indent_region_event(event)

    def comment_region_event(self,event=None):
        return self.get_current_editor().comment_region_event(event)

    def dedent_region_event(self, event=None):
        return self.get_current_editor().dedent_region_event(event)

    def uncomment_region_event(self, event=None):
        return self.get_current_editor().uncomment_region_event(event)

    def tabify_region_event(self, event=None):
        return self.get_current_editor().tabify_region_event(event)

    def untabify_region_event(self, event=None):
        return self.get_current_editor().untabify_region_event(event)

    def toggle_tabs_event(self, event=None):
        return self.get_current_editor().toggle_tabs_event(event)

    def goto_line_event(self, event=None):
        return self.get_current_editor().goto_line_event(event)

    def increase_font_size_event(self, event=None):
        edit = self.select()
        if edit:
            edit = self.get_current_editor()
            edit.change_font_size(self.parent.console, self.get_current_frame().get_line_widget(), lambda s: s + 2)


    def decrease_font_size_event(self, event=None):
        edit = self.select()
        if edit:
            edit = self.get_current_editor()
            edit.change_font_size(self.parent.console, self.get_current_frame().get_line_widget(), lambda s: s - 2)

