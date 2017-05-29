# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 10:43:45 2017

@author: 3605386
"""
import socket
import logging
from InterpreterServer.StudentInterpreter import StudentInterpreter
from InterpreterServer.FullInterpreter import FullInterpreter
import json
import sys
import os
from multiprocessing import Pipe, Process
from InterpreterServer.Parser import Parser
from InterpreterServer.Compiler import Compiler
from InterpreterServer.CheckAST import CheckAST
from InterpreterServer.Executor import Executor
import uuid

class RunServer():
    '''
    Server which treats client's requests according to the protocol
    '''
    def __init__(self):
        '''
        Initializes the server's socket accept connection
        from the client and starts the waiting loop
        '''
        logger = logging.getLogger("run_server")
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.buffer_size = 4096
        serverSocket.bind((host, 0))
        port = serverSocket.getsockname()[1]
        config_file = open("config.txt", "w")
        config_file.write(str(port))
        config_file.flush()
        logger.info("write")
        serverSocket.listen(10)
        logger.info("Listen")
        self.connexion, addresse = serverSocket.accept()
        os.remove("config.txt")
        logger.info("Listening on %s:%s..." % (host, str(port)))
        self.server_con, self.interpreter_conn = Pipe()
        self.parser = None
        self.compiler = None
        self.check_ast = None
        self.executor = None
        self.waitproc = None
        self.serverLoop()
        self.interpreter = None
    def waitResult(self, pipe):
        '''
        Waits the result from the interpreter and sends it to the client
        '''
        res = pipe.recv()
        self.connexion.send(res)

    def serverLoop(self):
        '''
        Waits for requests from the client and treat those requests
        '''
        self.newInterpreter(True)
        while True:
            data = self.connexion.recv(self.buffer_size)
            if(not data):
                self.connexion.close()
                self.interpreter.t1.terminate()
                return
            sdata = data.decode("Utf8")
            prot = json.loads(sdata)
            if(not ("msg_type" in prot.keys())):
                logger.error("miss msg_type key")
            elif(prot["msg_type"] == "interrupt"):
                if(not("session_id" in prot.keys()) or not("msg_id" in prot.keys()) or\
                    not("protocol_version" in prot.keys())):
                    logger.error("miss session_id or msg_id or protocol_version key")
                elif(self.interpreter.t1.is_alive()):
                    self.interpreter.t1.terminate()
                    if(self.waitproc.is_alive()):
                        self.waitproc.terminate()
                    self.interrupt_return(True, prot)
                    self.newInterpreter(True)
                else:
                    self.interrupt_return(False, prot)
            
            elif(prot["msg_type"]=="exec"):
                self.interpreter.t1.terminate()
                if(not("content" in prot.keys()) or not("mode" in prot["content"].keys())):
                    logger.error("miss content key or mode key")
                elif(prot["content"]["mode"] == "full"):
                    self.newInterpreter(False, prot)
                    self.waitproc = Process(target=self.waitResult, args=(self.server_con,))
                    self.waitproc.start()
                elif(prot["content"]["mode"] == "student"):
                    self.newInterpreter(True, prot)
                    self.waitproc = Process(target=self.waitResult, args=(self.server_con,))
                    self.waitproc.start()
                else:
                    logger.error("unknown mode")
            elif(prot["msg_type"] == "eval"):
                if(self.interpreter.t1.is_alive() and self.interpreter.type != prot["content"]["mode"]):
                    self.newInterpreter(prot["content"]["mode"] == "student")
                self.server_con.send(prot)
                self.waitproc = Process(target=self.waitResult, args=(self.server_con,))
                self.waitproc.start()
            else:
                logger.error("msg_type error")

    def newInterpreter(self, student, prot=None):
        '''
        Creates a new interpreter
        '''
        self.parser = Parser()
        self.compiler = Compiler()
        self.executor = Executor()
        if(student):
            self.check_ast = CheckAST()
            if(prot is None):
                self.interpreter = StudentInterpreter({}, self.interpreter_conn,
                                                      self.compiler, self.check_ast,
                                                      self.parser, self.executor)
            else:
                self.interpreter = StudentInterpreter(prot, self.interpreter_conn,
                                                      self.compiler, self.check_ast,
                                                      self.parser, self.executor)
        else:
            if(prot is None):
                self.interpreter = FullInterpreter({}, self.interpreter_conn,
                                                   self.compiler, self.parser, self.executor)
            else:
                self.interpreter = FullInterpreter(prot, self.interpreter_conn,
                                                   self.compiler, self.parser, self.executor)

    def interrupt_return(self,success,prot):
        '''
        Answers to an interrupt request from the client 
        '''
        retour = {}
        if(success):
            retour["msg_type"] = "interrupt_success"
        else:
            retour["msg_type"] = "interrupt_fail"
        retour["session_id"] = prot["session_id"]
        retour["msg_id"] = uuid.uuid1().int
        retour["protocol_version"] = prot["protocol_version"]
        retour["content"] = {}
        jsonRetour = json.dumps(retour)
        self.connexion.send(jsonRetour.encode("Utf8"))

if __name__ == "__main__":
    server = RunServer()
    server.serverLoop()
