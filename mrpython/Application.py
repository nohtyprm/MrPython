from MainView import MainView
from tkinter import Tk, sys
from PyEditor import PyEditor
import Bindings

class Application:
    """
    The main class of the application
    - root is the starting point of the GUI application
    - main_view defines the main window
    - py_editor_list defines the editor interface (from the main_view)
    - py_shell defines the shell interface (white and orange widgets)
    """
    
    def __init__(self):
        """ Set up some information like, set up the interfaces """
        self.root = Tk()
        self.root.title("MrPython")
        
        self.mode = "full"
        
        self.main_view = MainView(self.root)
        self.py_icons = self.main_view.py_icon_frame
        self.py_editor_list = self.main_view.py_editor_list
        self.py_shell = self.main_view.py_shell
        self.change_mode()

        self.apply_bindings()
        self.root.protocol('WM_DELETE_WINDOW', self.close_all_event)

    def run(self):
        self.main_view.show()

    def apply_bindings(self, keydefs=None):
        """ Bind the menu actions to the related event methods """
        self.new_file_button = self.py_icons.icon_new_file_label
        self.run_button = self.py_icons.icon_run_label
        self.save_button = self.py_icons.icon_save_label
        self.open_button = self.py_icons.icon_open_label
        self.mode_button = self.py_icons.icon_mode_label
        self.new_file_button.bind("<1>", self.new_file)
        self.run_button.bind("<1>", self.run_module)
        self.mode_button.bind("<1>", self.change_mode)
        self.save_button.bind("<1>", self.py_editor_list.save)
        self.open_button.bind("<1>", self.open)
        
        #file
        self.root.bind("<<open-new-window>>", self.new_file)
        self.root.bind('<<open-window-from-file>>', self.open)
        self.root.bind('<<save-window>>', self.py_editor_list.save)
        self.root.bind('<<save-window-as-file>>', self.py_editor_list.save_as)
        self.root.bind('<<save-copy-of-window-as-file>>',
                       self.py_editor_list.save_as_copy)
        self.root.bind('<<close-window>>',
                       self.py_editor_list.close_current_editor)
        self.root.bind('<<close-all-windows>>', self.close_all_event)

        #edit
        self.root.bind('<<undo>>', self.py_editor_list.undo_event)
        self.root.bind('<<redo>>', self.py_editor_list.redo_event)
        self.root.bind('<<cut>>', self.py_editor_list.cut_event)
        self.root.bind('<<copy>>', self.py_editor_list.copy_event)
        self.root.bind('<<paste>>', self.py_editor_list.paste_event)
        self.root.bind('<<select-all>>', self.py_editor_list.select_all_event)
        self.root.bind('<<find>>', self.py_editor_list.find_event)
        self.root.bind('<<find-again>>', self.py_editor_list.find_again_event)
        self.root.bind('<<find-selection>>',
                       self.py_editor_list.find_selection_event)
        self.root.bind('<<find-in-files>>',
                       self.py_editor_list.find_in_files_event)
        self.root.bind('<<replace>>', self.py_editor_list.replace_event)
        self.root.bind('<<goto-line>>', self.py_editor_list.goto_line_event)

        #format
        self.root.bind('<<indent-region>>',
                       self.py_editor_list.indent_region_event)
        self.root.bind('<<dedent-region>>',
                       self.py_editor_list.dedent_region_event)
        self.root.bind('<<comment-region>>',
                       self.py_editor_list.comment_region_event)
        self.root.bind('<<uncomment-region>>',
                       self.py_editor_list.uncomment_region_event)
        self.root.bind('<<tabify-region>>',
                       self.py_editor_list.tabify_region_event)
        self.root.bind('<<untabify-region>>',
                       self.py_editor_list.untabify_region_event)
        self.root.bind('<<toggle-tabs>>',
                       self.py_editor_list.toggle_tabs_event)
 
        #run
        self.root.bind('<<check-module>>', self.check_module)
        self.root.bind('<<run-module>>', self.run_module)
        self.root.bind('<Control-Key-Return>', self.run_source)

        #debug
        self.root.bind('<<goto-file-line>>',
                       self.py_editor_list.goto_line_event)

        # Show the tooltips of the shortcut icons when pressing Alt-Ctrl
        #self.root.bind('<

        #bindings keys
        if keydefs is None:
            keydefs = Bindings.default_keydefs
        for event, keylist in keydefs.items():
            if keylist:
                self.root.event_add(event, *keylist)

    def change_mode(self, event=None):
        if self.mode == "student":
            self.mode = "full"
        else:
            self.mode = "student"
        self.py_icons.switch_icon_mode(self.mode)
        self.py_shell.change_mode(self.mode)

    def new_file(self, event=None):
        """ Creates a new empty editor and put it into the pyEditorList """
        file_editor = PyEditor(self.py_editor_list)        
        self.py_editor_list.add(file_editor, text=file_editor.get_file_name())

    def open(self, event=None):
        file_editor = PyEditor(self.py_editor_list, open=True)
        if (self.py_editor_list.focusOn(file_editor.long_title()) == False):
            if (file_editor.isOpen()):
                self.py_editor_list.add(file_editor,
                                        text=file_editor.get_file_name())

    def close_all_event(self, event=None):
        while self.py_editor_list.get_size() > 0:
            reply = self.py_editor_list.close_current_editor()
            if reply == "cancel":
                break;
        if self.py_editor_list.get_size() == 0:
            sys.exit(0)

    def run_module(self, event=None):
        reply = self.py_editor_list.get_current_editor().maybesave_run()
        if (reply != "cancel"):
            file_name = self.py_editor_list.get_current_editor().long_title()
            self.py_shell.run(file_name)

    def check_module(self, event=None):
        reply = self.py_editor_list.get_current_editor().maybesave_run()
        if (reply != "cancel"):
            self.py_shell.check(self.py_editor_list.get_current_editor())

    def run_source(self,event=None):
        file_name = self.py_editor_list.get_current_editor().long_title()
        self.py_shell.runit(file_name)

if __name__ == "__main__":
    app = Application()
    app.run()  
