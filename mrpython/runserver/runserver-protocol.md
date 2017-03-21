
Protocole Client Serveur
===================

Format des messages
-------------------------------

### En-tête du message

```python
{
   "session_id" : uuid # identifiant de la session (session = instance de l'interprète)
  , "msg_id" : uuid # identifiant unique du message
  , "msg_type : str # type de message (évaluation, etc.)
  , "protocol_version": str # exemple : "0.1"
  , "content" : json, # contenu du message 
}
```

Structure "data"
---------------------

Encodage des valeurs retournées par le RunServer:

    { "data": [ { "mime" : str  # type mime du résultat (ex. text, text/html,
	                            # image/png, etc.)
	              "value" : str # encodage des données
	            } ... ] }

Evaluation d'une expression
---------------------------------------

### 1. Emission par MrPython

	 {...
	  "msg_type": "eval"
	  "content": {
	               "expr": str # expression à évaluer
	               "mode": "student" | "full"
	             }
     }
				   

### 2. Retour par RunServer

  - variante 1 : succès

    {...
	"msg_type": "eval_success"
	  "content": {
	               "data": data # valeur(s) retournées (cf. structure "data")
				   "stdout" : str # sorties standard
				   "stderr" : str # sorties erreur
				   "report" : [ ... cf. "error" (mais que des warnings) ]
	             }
     }


   - variante 2 : erreur
   
    {...
	"msg_type": "eval_error"
	  "content": {
	               "report":  [ 
				     { "error_type": "exception" | "student"
	               "traceback": tb # cf. module traceback (décodage de toutes les infos potentiellement utile sur l'erreur) pour les erreurs "exception"
				   # ou alors, pour les erreurs "student"
				   "infos":  { "student_error_type": str
				                "severity" : "error" | "warning"
				                    "description": json # en fonction du type d'erreur
   							  } ... ]
                  } 
       }
	 }
				   
## Exécution d'un programme



## Interruption de l'éxécution
### MrPython
	{"cmd": "interrupt",
	 "filename":"nom du fichier",
	 "source":"code source",
	 "mode":"student"}
ou

	{"cmd": "interrupt",
	 "filename":"nom du fichier",
	 "source":"code source",
	 "mode":"full"}
###RunServer

	{"status":"success",
	  "output":"rapport d'exécution"}
ou

	{"status":"failure",
	 "output":"rapport d'exécution"}

##Interface Graphique
###MrPython
	{"cmd": "graphics",
	 "filename":"nom du fichier",
	 "source":"code source",
	 "mode":"student"}
###RunServer
	{"status": "success"
	 "output":"parametres de création de la figure"}
ou

	{"status":"failure",
	 "output":"rapport d'exécution"}

##Input
###MrPython
	{"cmd": "input",
	 "filename":"nom du fichier",
	 "source":"code source",
	 "mode":"student"}
ou

	{"cmd": "input",
	 "filename":"nom du fichier",
	 "source":"code source",
	 "mode":"full"}
###RunServer

	{"cmd":"inputValues"}
