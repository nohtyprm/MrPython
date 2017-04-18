# Définition d'un client réseau rudimentaire
# Ce client dialogue avec un serveur ad hoc
 
import socket, sys
import json
from threading import Thread
HOST = socket.gethostname()
PORT = 5000

# 1) création du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# 2) envoi d'une requête de connexion au serveur :
try:
  mySocket.connect((HOST, PORT))
except socket.error:
  print("La connexion a échoué.")
  sys.exit()
print("Connexion établie avec le serveur.")

class PrintThread(Thread):

    """Thread chargé simplement d'éxécuter un thread."""

    def __init__(self):
        Thread.__init__(self)
        

    def run(self):
        """Code à exécuter pendant l'exécution du thread."""
        while True:
            msgServeur=mySocket.recv(1024).decode("Utf8")
            if(not msgServeur):
                mySocket.close()
                return
            prot=json.loads(msgServeur)
            print(prot)
            
# 3) Dialogue avec le serveur :
msgServeur = mySocket.recv(1024).decode("Utf8")
t=PrintThread()
t.start()
mon_fichier = open("test.txt", "r")
contenu = mon_fichier.read()
mon_fichier.close()

#docJson ={ "session_id": 1, "msg_id": 1, "msg_type" : "exec", "protocol_version": 0.1, "content" : {"source" : contenu, "mode": "full" }}
##docJson = {"execOrEval" : "exec", "filename" : "test.txt", "source" : "testReturn.txt", "mode" : "full"}
#docJson2 = json.dumps(docJson)
#print("S>", msgServeur)
#msgClient = docJson2
#mySocket.send(msgClient.encode("Utf8"))

#vcfmsgServeur = mySocket.recv(1024).decode("Utf8")
#retour=json.loads(vcfmsgServeur)
#content=retour["content"]
#if(retour["msg_type"]=="exec_success"):
#    print("cedric")
#    print(content["stdout"])
#    print(content["stderr"])
#if(retour["msg_type"]=="exec_error"):
#    print(content["stdout"])
#    print(content["stderr"])
#    print(content["report"])

inter ={ "session_id": 1, "msg_id": 1, "msg_type" : "interrupt", "protocol_version": 0.1}
inter2 = json.dumps(inter)
msgClient = inter2
mySocket.send(msgClient.encode("Utf8"))
t.join()
# 4) Fermeture de la connexion :
print("Connexion interrompue.")

