# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 10:43:45 2017

@author: 3605386
"""
import socket
import logging
from PSTL_MrPython_Client_Serveur.StudentInterpreter import StudentInterpreter
from PSTL_MrPython_Client_Serveur.FullInterpreter import FullInterpreter
import json
import sys
import os
from multiprocessing import Pipe, Process
from PSTL_MrPython_Client_Serveur.Parser import Parser
from PSTL_MrPython_Client_Serveur.Compiler import Compiler
from PSTL_MrPython_Client_Serveur.CheckAST import CheckAST
from PSTL_MrPython_Client_Serveur.Executor import Executor

class RunServer():
    def __init__(self):
        logger = logging.getLogger("run_server")
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.buffer_size = 4096
        serverSocket.bind((host, 0)) #Prend le premier port disponible
        port = serverSocket.getsockname()[1] #numero du port
        config_file = open("config.txt", "w")
        config_file.write(str(port))
        config_file.flush()
        logger.info("write") #logger.info n'affiche rien à l'écran contrairement à logger.warning

        serverSocket.listen(10)
        logger.info("Listen")
        self.connexion, addresse = serverSocket.accept()
        os.remove("config.txt")
        logger.warning("accept")
        logger.info("Listening on %s:%s..." % (host, str(port)))
        self.serverLoop()
    def waitResult(self, pipe):
        pass
        res = pipe.recv()
        self.connexion.send(res)

    def serverLoop(self):

        server_con, interpreter_conn = Pipe()
        parser = Parser()
        compiler = Compiler()
        check_ast = CheckAST()
        executor = Executor()
        self.interpreter = StudentInterpreter({}, interpreter_conn, \
        compiler, check_ast, parser, executor)
        while True:
            data = self.connexion.recv(self.buffer_size) #attend trop à la récéption
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
                    retour={}
                    retour["msg_type"]="interrupt_success"
                    retour["session_id"]=  prot["session_id"]
                    retour["msg_id"]=prot["msg_id"]+1
                    retour["protocol_version"]=prot ["protocol_version"]
                    retour["content"]={}
                    jsonRetour = json.dumps(retour)
                    self.connexion.send(jsonRetour.encode("Utf8"))
                else:
                    retour={}
                    retour["msg_type"] = "interrupt_fail"
                    retour["session_id"] = prot["session_id"]
                    retour["msg_id"] = prot["msg_id"]+1
                    retour["protocol_version"] = prot["protocol_version"]
                    retour["content"] = {}
                    jsonRetour = json.dumps(retour)
                    self.connexion.send(jsonRetour.encode("Utf8"))
            elif(prot["msg_type"]=="exec"):
                self.interpreter.t1.terminate()
                if(not("content" in prot.keys()) or not("mode" in prot["content"].keys())):
                    logger.error("miss content key or mode key")
                elif(prot["content"]["mode"] == "full"):
                    self.interpreter = FullInterpreter(prot, interpreter_conn,compiler,check_ast,parser,executor)
                    waitproc=Process(target=self.waitResult,args=(server_con,))
                    waitproc.start()
                elif(prot["content"]["mode"] == "student"):
                    self.interpreter = StudentInterpreter(prot, interpreter_conn,compiler,check_ast,parser,executor)
                    waitproc=Process(target=self.waitResult,args=(server_con,))
                    waitproc.start()
                else:
                    logger.error("unknown mode")
            elif(prot["msg_type"] == "eval"):
                server_con.send(prot)
                waitproc=Process(target=self.waitResult,args=(server_con,))
                waitproc.start()
            else:
                logger.error("msg_type error")
            
                

if __name__ == "__main__":
    server = RunServer()
    server.serverLoop()
