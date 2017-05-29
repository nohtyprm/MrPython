# -*- coding: utf-8 -*-
"""
Created on Fri May 26 16:25:20 2017

@author: 3301202
"""
import logging
import os
from multiprocessing import Process
from InterpreterServer.RunReport import RunReport
from InterpreterServer.Parser import Parser
from InterpreterServer.CheckAST import CheckAST
from InterpreterServer.Compiler import Compiler
from InterpreterServer.Executor import Executor
from InterpreterServer.Reporter import Reporter
from translate import tr
import json
import uuid
class VirtualExecProcess(Process):
    def __init__(self):
        Process.__init__(self)

    def compileExec(self, prot, student):
        '''
        Compute the result of a "exec" or "eval" request and send it to the server
        '''
        while(True):
            error = False
            ret = {}
            if(prot == {}):
                prot = self.pipe.recv()
            if(prot["msg_type"] == "exec"):
                ret["content"], error = self._computeOutExec(prot["content"], "exec", student)
                ret["session_id"] = prot["session_id"]
                ret["msg_id"] = uuid.uuid1().int
                if(error == True):
                    ret["msg_type"] = "exec_error"
                else:
                    ret["msg_type"] = "exec_success"
                ret["protocol_version"] = prot["protocol_version"]
                jsonRetour = json.dumps(ret)
                self.pipe.send(jsonRetour.encode("Utf8"))
            elif(prot["msg_type"] == "eval"):
                ret["content"], error = self._computeOutExec(prot["content"], "eval", student)
                ret["session_id"] = prot["session_id"]
                ret["msg_id"] = uuid.uuid1().int
                if(error == True):
                    ret["msg_type"] = "eval_error"
                else:
                    ret["msg_type"] = "eval_success"
                ret["protocol_version"] = prot["protocol_version"]
                jsonRetour = json.dumps(ret)
                self.pipe.send(jsonRetour.encode("Utf8"))
            prot = {}

    def _computeOutExec(self, contenu, typ,student):
        '''
        Run a code or an expression and return the result 
        '''
        if(student):
            logger = logging.getLogger("StudentInterpreter")
        else:
            logger = logging.getLogger("FullInterpreter")
        if(typ == "eval"):
            if(not("expr" in contenu.keys()) or not("filename" in contenu.keys())):
                logger.error("miss key 'expr' or 'filename' in contenu")
            else:
                error = False
                retcontent = {}
                report = self.init_report(False, contenu)
                reporter = Reporter()
                #compile
                code, report = self.compiler.compile(contenu["expr"],
                                                     report, typ, contenu["filename"])
                if(code==None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #evaluate
                report, out_str, err_str, error = self.executor.execute(code, report,False)
                if(error==True):
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #retour
                retcontent["stderr"] = err_str
                retcontent["stdout"] = out_str
                #retcontent["data"] = data
                retcontent["report"] = reporter.compute_report(report)
                return retcontent, error
                
        elif(typ == "exec"):
            if(not("source" in contenu.keys()) or not("filename" in contenu.keys())):
                logger.error("miss key 'source' or 'filename' in contenu")
            else:
                error = False
                retcontent = {}
                report = self.init_report(True, contenu)
                reporter = Reporter()
                #Parser
                ast, report = self.parser.parse(contenu["source"], report, contenu["filename"])
                if(ast == None):
                    error = True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                #check
                if(student):
                    ast, report = self.parser.parse(contenu["source"], report, 
                                                    contenu["filename"])
                    if(ast == None):
                        error = True
                        retcontent["report"] = reporter.compute_report(report)
                        return retcontent, error

                #compile
                code, report = self.compiler.compile(ast, report, typ, contenu["filename"])
                if(code==None):
                    error=True
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error

                #executor
                report, out_str, err_str,error = self.executor.execute(code, report,True)
                if(error):
                    retcontent["report"] = reporter.compute_report(report)
                    return retcontent, error
                    
                retcontent["stderr"] = err_str
                retcontent["stdout"] = out_str
                retcontent["report"] = reporter.compute_report(report)
                return retcontent, error

    def init_report(self,execute,contenu):
        '''
        Initialise a RunReport with corresponding header and footer
        '''
        report = RunReport()
        if(execute):
            begin_report = "=== " + tr("Interpretation of: ") +\
             os.path.basename(contenu["filename"]) + " ===\n"
        else:
            begin_report = "=== " + tr("Evaluating: ") + "'" + contenu["expr"] + "' ===\n"
        report.set_header(begin_report)
        end_report = "\n" + ('=' * len(begin_report)) + "\n\n"
        report.set_footer(end_report)
        return report

    def run(self):
        raise NotImplementedError
    
