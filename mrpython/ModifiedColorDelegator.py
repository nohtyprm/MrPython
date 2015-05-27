from ColorDelegator import ColorDelegator

class ModifiedColorDelegator(ColorDelegator):
    "Extend base class: colorizer for the shell window itself"

    def __init__(self):
        ColorDelegator.__init__(self)
        self.LoadTagDefs()

    def recolorize_main(self):
        self.tag_remove("TODO", "1.0", "iomark")
        self.tag_add("SYNC", "1.0", "iomark")
        ColorDelegator.recolorize_main(self)

    def LoadTagDefs(self):
        ColorDelegator.LoadTagDefs(self)
        theme = MrPythonConf.GetOption('main','Theme','name')
        self.tagdefs.update({
            "stdin": {'background':None,'foreground':None},
            "stdout": MrPythonConf.GetHighlight(theme, "stdout"),
            "stderr": MrPythonConf.GetHighlight(theme, "stderr"),
            "console": MrPythonConf.GetHighlight(theme, "console"),
        })

    def removecolors(self):
        # Don't remove shell color tags before "iomark"
        for tag in self.tagdefs:
            self.tag_remove(tag, "iomark", "end")
