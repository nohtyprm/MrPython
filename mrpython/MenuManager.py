from tkinter import *
from PyEditor import PyEditor


class MenuManager:
    import Bindings
    def __init__(self,parent):
        self.parent=parent
        self.menu_specs = [
            ("file", "_File"),
            ("edit", "_Edit"),
            ("format", "F_ormat"),
            ("shell", "She_ll"),
            ("run", "_Run"),
            ("debug", "_Debug"),
            ("options", "_Options"),
            ("windows", "_Window"),
            ("help", "_Help"),
        ]

    def createmenubar(self):
        parent=self.parent

        parent.menubar=Menu(parent.root)

        self.menudict = menudict = {}
        for name, label in self.menu_specs:
            underline, label = prepstr(label)
            menudict[name] = menu = Menu(parent.menubar, name=name)
            parent.menubar.add_cascade(label=label, menu=menu, underline=underline)
        self.fill_menus()
        parent.recent_files_menu = Menu(parent.menubar)
        self.menudict['file'].insert_cascade(3, label='Recent Files',
                                             underline=0,
                                             menu=parent.recent_files_menu)
        parent.root.config(menu=parent.menubar)

    def fill_menus(self):
        #import pdb ; pdb.set_trace()
        menudefs = self.Bindings.menudefs
        keydefs=self.Bindings.default_keydefs
        menudict = self.menudict

        for mname, entrylist in menudefs:
            menu = menudict.get(mname)
            if not menu:
                continue
            for entry in entrylist:
                if not entry:
                    menu.add_separator()
                else:
                    label, eventname = entry
                    checkbutton = (label[:1] == '!')
                    if checkbutton:
                        label = label[1:]
                    underline, label = prepstr(label)
                    accelerator = get_accelerator(keydefs, eventname)
                    def command(text=self.parent.view, eventname=eventname):
                        text.event_generate(eventname)

                    if checkbutton:
                        menu.add_command(label=label,underline=underline,command=command,accelerator=accelerator)
                    else:
                        menu.add_command(label=label,underline=underline,command=command,accelerator=accelerator)


keynames = {
 'bracketleft': '[',
 'bracketright': ']',
 'slash': '/',
}

def get_accelerator(keydefs, eventname):
    keylist = keydefs.get(eventname)
    # issue10940: temporary workaround to prevent hang with OS X Cocoa Tk 8.5
    # if not keylist:
    if (not keylist) or (eventname in {
                            "<<open-module>>",
                            "<<goto-line>>",
                            "<<change-indentwidth>>"}):
        return ""
    s = keylist[0]
    s = re.sub(r"-[a-z]\b", lambda m: m.group().upper(), s)
    s = re.sub(r"\b\w+\b", lambda m: keynames.get(m.group(), m.group()), s)
    s = re.sub("Key-", "", s)
    s = re.sub("Cancel","Ctrl-Break",s)   # dscherer@cmu.edu
    s = re.sub("Control-", "Ctrl-", s)
    s = re.sub("-", "+", s)
    s = re.sub("><", " ", s)
    s = re.sub("<", "", s)
    s = re.sub(">", "", s)
    return s

def prepstr(s):
    # Helper to extract the underscore from a string, e.g.
    # prepstr("Co_py") returns (2, "Copy").
    i = s.find('_')
    if i >= 0:
        s = s[:i] + s[i+1:]
    return i, s
