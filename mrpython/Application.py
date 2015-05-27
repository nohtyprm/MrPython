from MainView import MainView
from tkinter import *
from PyEditor import PyEditor
from PyEditorList import PyEditorList
from PyShell import  PyShell
import Bindings
#test git

def main():
    app = Application()
    app.run()

class Application:
    def __init__(self):

        self.root=Tk()
        self.root.title("MrPyton2.0")

        self.main_view=MainView(self.root)
        self.pyEditorList=self.main_view.pyEditorList
        self.pyShell=self.main_view.pyShell

        self.apply_bindings()
        self.root.protocol('WM_DELETE_WINDOW',self.close_all_event)

    def run(self):
        self.main_view.show()

    def apply_bindings(self, keydefs=None):
        #bindings event
        #file
        self.root.bind("<<open-new-window>>", self.newfile)
        self.root.bind('<<open-window-from-file>>',self.open)
        self.root.bind('<<save-window>>',self.pyEditorList.save)
        self.root.bind('<<save-window-as-file>>',self.pyEditorList.save_as)
        self.root.bind('<<save-copy-of-window-as-file>>',self.pyEditorList.save_as_copy)

        self.root.bind('<<close-window>>',self.pyEditorList.close_current_editor)
        self.root.bind('<<close-all-windows>>',self.close_all_event)

        #edit
        self.root.bind('<<undo>>',self.pyEditorList.undo_event)
        self.root.bind('<<redo>>',self.pyEditorList.redo_event)
        self.root.bind('<<cut>>',self.pyEditorList.cut_event)
        self.root.bind('<<copy>>',self.pyEditorList.copy_event)
        self.root.bind('<<paste>>',self.pyEditorList.paste_event)
        self.root.bind('<<select-all>>',self.pyEditorList.select_all_event)
        self.root.bind('<<find>>',self.pyEditorList.find_event)
        self.root.bind('<<find-again>>',self.pyEditorList.find_again_event)
        self.root.bind('<<find-selection>>',self.pyEditorList.find_selection_event)
        self.root.bind('<<find-in-files>>',self.pyEditorList.find_in_files_event)
        self.root.bind('<<replace>>',self.pyEditorList.replace_event)
        self.root.bind('<<goto-line>>',self.pyEditorList.goto_line_event)

        # #format
        self.root.bind('<<indent-region>>',self.pyEditorList.indent_region_event)
        self.root.bind('<<dedent-region>>',self.pyEditorList.dedent_region_event)
        self.root.bind('<<comment-region>>',self.pyEditorList.comment_region_event)
        self.root.bind('<<uncomment-region>>',self.pyEditorList.uncomment_region_event)
        self.root.bind('<<tabify-region>>',self.pyEditorList.tabify_region_event)
        self.root.bind('<<untabify-region>>',self.pyEditorList.untabify_region_event)
        self.root.bind('<<toggle-tabs>>',self.pyEditorList.toggle_tabs_event)
 
        # #run
        self.root.bind('<<check-module>>',self.check_module)
        self.root.bind('<<run-module>>',self.run_module)
        self.root.bind('<Control-Key-Return>',self.run_source)

        # #debug
        self.root.bind('<<goto-file-line>>',self.pyEditorList.goto_line_event)


        #bindings keys
        if keydefs is None:
            keydefs=Bindings.default_keydefs
        for event, keylist in keydefs.items():
            if keylist:
                self.root.event_add(event, *keylist)



    def newfile(self,event=None):
        fileEditor=PyEditor(self.main_view.pyEditorList)
        self.pyEditorList.add(fileEditor,text=fileEditor.get_file_name())

    def open(self, event=None):
        fileEditor=PyEditor(self.main_view.pyEditorList,open=True)
        if(self.pyEditorList.focusOn(fileEditor.long_title())==False):
            if(fileEditor.isOpen()):
                self.pyEditorList.add(fileEditor,text=fileEditor.get_file_name())

    def close_all_event(self,event=None):
        while self.pyEditorList.get_size()>0 :
            reply = self.pyEditorList.close_current_editor()
            if reply == "cancel":
                break;

        if self.pyEditorList.get_size()==0:
            sys.exit(0)

    def run_module(self,event=None):
        reply=self.pyEditorList.get_current_editor().maybesave_run()
        if(reply!="cancel"):
            filename=self.pyEditorList.get_current_editor().long_title()
            self.pyShell.run(filename)

    def check_module(self,event=None):
        reply=self.pyEditorList.get_current_editor().maybesave_run()
        if(reply!="cancel"):
            self.pyShell.check(self.pyEditorList.get_current_editor())        

    def run_source(self,event=None):
        filename=self.pyEditorList.get_current_editor().long_title()
        self.pyShell.runit(filename)

if __name__ =="__main__":
    main()
