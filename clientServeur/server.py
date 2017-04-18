import socket
import json
import sys
import py_compile

def _compileExec(execOrEval, contenu, out,err, mode):
    error = False
    content={}
    if(mode == "full"):
        if(execOrEval == "exec"):
            #mon_fichier = open(filename, "r")
            #contenu = mon_fichier.read()
            #mon_fichier.close()
        
            fst_stdout=sys.stdout
            fst_stderr=sys.stderr
            sys.stdout = open(out, 'w+')
            sys.stderr=open(err,'w+')
            
            code = compile(contenu,'', 'exec')#on écrit la sortie std out dans out  et stderr dans err  
         
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
            content["stdout"]=out_str
            content["stderr"]=err_str
            #TODO gestion erreurs
		
        else:
            #TODO : mode eval
            pass
    else:
        #TODO: mode student
        pass
    return content,tb,error
    
    
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
data = connexion.recv(buffer_size)
retour ={}
sdata = data.decode("Utf8")
test = json.loads(sdata)
session_id=test["session_id"]
msg_id=test["msg_id"]
msg_type=test["msg_type"]
protocol_version=test["protocol_version"]
content=test["content"]
source=content["source"]
mode=content["mode"]
#print(session_id)
#print(msg_id)
#print(msg_type)
#print(protocol_version)
#print(content)
#print(source)
#print(mode)

#execOrEval = test["execOrEval"]
#filename = test["filename"]
#source = test["source"]
#mode = test["mode"]
#retour["output"] , retour["status"] = _compileExec(execOrEval, filename, source, mode)
retour={}
retour["session_id"]=session_id
retour["msg_id"]=msg_id+1

retour["protocol_version"]=protocol_version
retour["content"],tb,error=_compileExec("exec",source,"out.txt","err.txt",mode)
#print(out)
#print(err)
#print(tb)
if(error==False):
    retour["msg_type"]="exec_success"
#    retour["content"]={"stdout": out,"stderr": err}#+report:warnings
#    
#    print(type(out))

    pass
else:
    retour["msg_type"]="exec_error"
#    
#    retour["content"]={"stdout": out,"stderr": err,"report":{"error_type":"exception","traceback":tb}}
    pass
    
jsonRetour = json.dumps(retour)
connexion.send(jsonRetour.encode("Utf8"))
connexion.close()

