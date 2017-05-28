
from InterpreterServer.VirtualExecProcess import VirtualExecProcess

class FullExecProcess(VirtualExecProcess):
    def __init__(self, prot, pipe, compiler, parser, executor):
        VirtualExecProcess.__init__(self)
        self.prot = prot
        self.compiler = compiler
        self.parser = parser
        self.executor = executor
        self.pipe = pipe

    def run(self):
        self.compileExec(self.prot, False)

class FullInterpreter():
    def __init__(self, prot, pipe, compiler, parser, executor):
        self.pipe = pipe
        self.compiler = compiler
        self.executor = executor
        self.parser = parser
        self.t1 = FullExecProcess(prot, pipe, compiler, parser, executor)
        self.t1.start()
        self.type = "full"
