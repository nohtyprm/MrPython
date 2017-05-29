# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 10:50:13 2017

@author: 3605386
"""

from InterpreterServer.VirtualExecProcess import VirtualExecProcess


class StudentExecProcess(VirtualExecProcess):



    def __init__(self, prot, pipe, compiler, check_ast, parser, executor):
        VirtualExecProcess.__init__(self)
        self.prot = prot
        self.compiler = compiler
        self.check_ast = check_ast
        self.parser = parser
        self.executor = executor
        self.pipe = pipe


    def run(self):
        self.compileExec(self.prot, True)

class StudentInterpreter():
    def __init__(self, prot, pipe, compiler, check_ast, parser, executor):
        self.pipe = pipe
        self.compiler = compiler
        self.check_ast = check_ast
        self.executor = executor
        self.parser = parser
        self.t1 = StudentExecProcess(prot, pipe, compiler, check_ast, parser, executor)
        self.t1.start()
        self.type = "student"
