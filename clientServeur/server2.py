# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:23:26 2017

@author: 3301202
"""

import socket
import json
import sys
import py_compile

from threading import Thread
from multiprocessing import Process


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 5000

buffer_size = 4096

serverSocket.bind((host, port))
serverSocket.listen(10)
connexion, addresse = serverSocket.accept()
msgServeur ="Vous êtes connecté au serveur"
connexion.send(msgServeur.encode("Utf8"))
print("Listening on %s:%s..." % (host, str(port)))


def _compileExec(prot):
    error = False
    ret={}
    if(prot["content"]["mode"] == "full"):
        if(prot["msg_type"] == "exec"):
            
        
            fst_stdout=sys.stdout
            fst_stderr=sys.stderr
            sys.stdout = open("out.txt", 'w+')
            sys.stderr=open("err.txt",'w+')
            
            code = compile(prot["content"]["source"],'', 'exec')#on écrit la sortie std out dans out  et stderr dans err  
         
            exec(code)
            sys.stdout.seek(0)
            sys.stderr.seek(0)
            out_str=sys.stdout.read()
            err_str=sys.stderr.read()
            sys.stdout=fst_stdout
            sys.stderr=fst_stderr
            a, b, tb = sys.exc_info() 
            if(len(err_str)>0):	
                error=True
            ret["content"]={}
            ret["content"]["stdout"]=out_str
            ret["content"]["stderr"]=err_str
            #TODO gestion erreurs
            ret["session_id"]=prot["session_id"]+1
            ret["msg_id"]=prot["msg_id"]+1
            
            ret["protocol_version"]=prot["protocol_version"]
            if(error==True):
                ret["msg_type"]="exec_error"
                ret["content"]["report"]=tb
            else:
                ret["msg_type"]="exec_success"
            jsonRetour = json.dumps(ret)
            connexion.send(jsonRetour.encode("Utf8"))
        else:
            #TODO : mode eval
            pass
    else:
        #TODO: mode student
        pass
   


class ExecProcess(Process):

    

    def __init__(self, prot):
        Process.__init__(self)
        self.prot = prot

    def run(self):
        
        _compileExec(self.prot)
        
       
#exec_proc=Process(target=_compileExec,args=({}))
mon_fichier = open("loop.txt", "r")
contenu = mon_fichier.read()
mon_fichier.close()       
docJson ={ "session_id": 1, "msg_id": 1, "msg_type" : "exec", "protocol_version": 0.1, "content" : {"source" : contenu, "mode": "full" }}
       
t1=ExecProcess(docJson)
t1.start()

def serverLoop(t1):
    while True:
        data=connexion.recv(buffer_size)
        if(not data):
            connexion.close()
            return
        sdata = data.decode("Utf8")
        test = json.loads(sdata)
        if(test["msg_type"]=="interrupt"):
            
            if(t1.is_alive()):
                t1.terminate()
                retour={}
                retour["msg_type"]="interrupt_success"
                retour["session_id"]=test["session_id"]
                retour["msg_id"]=test["msg_id"]+1
                retour["protocol_version"]=test ["protocol_version"]
                retour["content"]={}
                jsonRetour = json.dumps(retour)
                connexion.send(jsonRetour.encode("Utf8"))
            else:
                retour={}
                retour["msg_type"]="interrupt_fail"
                retour["session_id"]=test["session_id"]
                retour["msg_id"]=test["msg_id"]+1
                retour["protocol_version"]=test["protocol_version"]
                retour["content"]={}
                jsonRetour = json.dumps(retour)
                connexion.send(jsonRetour.encode("Utf8"))
        elif(test["msg_type"]=="exec"):
            #exec_proc=Process(target=_compileExec,args=(test))
            t1=ExecProcess(test)
            t1.start()

serverLoop(t1)
                
             
        
   

#connexion.close()

