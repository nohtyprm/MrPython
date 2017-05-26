# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 10:50:13 2017

@author: 3605386
"""
from multiprocessing import Process
import logging
import os
import json
from PSTL_MrPython_Client_Serveur.RunReport import RunReport
from PSTL_MrPython_Client_Serveur.Parser import Parser
from PSTL_MrPython_Client_Serveur.CheckAST import CheckAST
from PSTL_MrPython_Client_Serveur.Compiler import Compiler
from PSTL_MrPython_Client_Serveur.Executor import Executor
from PSTL_MrPython_Client_Serveur.Reporter import Reporter
from translate import tr
logger = logging.getLogger("StudentInterpreter")

class StudentExecProcess(Process):



    def __init__(self, prot, pipe, compiler, check_ast, parser, executor):
        Process.__init__(self)
        self.prot = prot
        self.compiler = compiler
        self.check_ast = check_ast
        self.parser = parser
        self.executor = executor
        self.pipe = pipe


    def run(self):
        self.compileExec(self.prot)
        
    def _computeOutExec(self, contenu, typ):

        if (typ == "eval"):
            if(not("expr" in contenu.keys()) or not("filename" in contenu.keys())):
                logger.error("miss key 'expr' or 'filename' in contenu")
            else:
                error = False
                retcontent = {}

                report = RunReport()
                reporter = Reporter()
                begin_report = "=== " + tr("Evaluating: ") + "'" + contenu["expr"] + "' ===\n"
                report.set_header(begin_report)
                end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
                report.set_footer(end_report)

                code,report=self.compiler.compile(contenu["expr"], report, typ, contenu["filename"])
                if(code == None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                data, report, out_str, err_str, error = self.executor.evaluate(code, report)
                if(error == True):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                retcontent["stderr"] = err_str
                retcontent["stdout"] = out_str
                retcontent["data"] = data
                retcontent["report"] = reporter.compute_report(report)
                return retcontent, error
        elif(typ == "exec"):
            if(not("source" in contenu.keys()) or not("filename" in contenu.keys())):
                logger.error("miss key 'source' or 'filename' in contenu")
            else:
                error = False
                retcontent = {}

                report = RunReport()
                begin_report = "=== " + tr("Interpretation of: ") + "'" +\
                    os.path.basename(contenu["filename"]) + "' ===\n"
                report.set_header(begin_report)
                end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
                report.set_footer(end_report)

                reporter = Reporter()
                #Parser
                ast, report = self.parser.parse(contenu["source"], report, contenu["filename"])
                if(ast == None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #check
                ast, report = self.check_ast.check(ast, report)
                if(ast == None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #compilee
                code, report = self.compiler.compile(ast, report, typ, contenu["filename"])
                if(code == None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #executor
                error, report, out_str, err_str = self.executor.execute(code, report)
                if(error):
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                retcontent["stderr"] = err_str
                retcontent["stdout"] = out_str
                retcontent["report"] = reporter.compute_report(report)
                return retcontent, error

    def compileExec(self, prot):
        while(True):
            error = False
            ret = {}
            if(prot == {}):
                prot = self.pipe.recv()
            if(prot["msg_type"] == "exec"):
                ret["content"], error = self._computeOutExec(prot["content"], "exec")
                ret["session_id"] = prot["session_id"] + 1
                ret["msg_id"] = prot["msg_id"] + 1
                if(error == True):
                    ret["msg_type"] = "exec_error"
                else:
                    ret["msg_type"] = "exec_success"
                ret["protocol_version"] = prot["protocol_version"]
                jsonRetour = json.dumps(ret)
                #mettre sur le pipe : le truc dumpé
                self.pipe.send(jsonRetour.encode("Utf8"))
            elif(prot["msg_type"] == "eval"):
                ret["content"], error = self._computeOutExec(prot["content"], "eval")
                ret["session_id"] = prot["session_id"]+1
                ret["msg_id"] = prot["msg_id"] + 1
                if(error == True):
                    ret["msg_type"] = "eval_error"
                else:
                    ret["msg_type"] = "eval_success"
                ret["protocol_version"] = prot["protocol_version"]
                jsonretour = json.dumps(ret)
                self.pipe.send(jsonretour.encode("Utf8"))
            prot = {}

class StudentInterpreter():
    def __init__(self, prot, pipe, compiler, check_ast, parser, executor):
        self.pipe = pipe
        self.compiler = compiler
        self.check_ast = check_ast
        self.executor = executor
        self.parser = parser
        self.t1 = StudentExecProcess(prot, pipe, compiler, check_ast, parser, executor)
        self.t1.start()
