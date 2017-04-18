# Définition d'un client réseau rudimentaire
# Ce client dialogue avec un serveur ad hoc
 
import socket, sys
import json
 
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
 
# 3) Dialogue avec le serveur :
msgServeur = mySocket.recv(1024).decode("Utf8")
mon_fichier = open("test.txt", "r")
contenu = mon_fichier.read()
mon_fichier.close()

docJson = docJson ={ "session_id": 1, "msg_id": 1, "msg_type" : "exec", "protocol_version": 0.1,\
                 "content" :{"source" : contenu, "mode": "full" }}
docJson2 = json.dumps(docJson)
print("S>", msgServeur)
msgClient = docJson2
mySocket.send(msgClient.encode("Utf8"))
msgServeur = mySocket.recv(1024).decode("Utf8")
print(msgServeur)
 
# 4) Fermeture de la connexion :
print("Connexion interrompue.")
mySocket.close()
