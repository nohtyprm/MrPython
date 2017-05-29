
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


    ```	
    {...
	"msg_type": "eval_success"
	  "content": {
	               "data": data # valeur(s) retournées (cf. structure "data")
				   "stdout" : str # sorties standard
				   "stderr" : str # sorties erreur
				   "report" : [ ... cf. "error" (mais que des warnings) ]
	             }
    }
    ```




   - variante 2 : erreur
   


    ```
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

    ```

	 
				   
## Exécution d'un programme
### 1. Emission par MrPython

    {...
	  "msg_type": "exec"
	  "content": {
	               "source": str # code source à éxecuter
	               "mode": "student" | "full"
	             }
     }
				   

### 2. Retour par RunServer

  - variante 1 : succès

    ```
    {...
	"msg_type": "exec_success"
	  "content": {
	               
				   "stdout" : str # sorties standard
				   "stderr" : str # sorties erreur
				   "report" : [ ... cf. "error" (mais que des warnings) ]
	             }
     }
    ```

   - variante 2 : erreur
   
    ```
    {...
	"msg_type": "exec_error"
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
    ``` 


## Interruption de l'éxécution
### 1. Emission par MrPython

    {...
	  "msg_type": "interrupt"
	   
     }

### 2. Retour par RunServer

    {...
	"msg_type": "interrupt_return"
	 
    }
   
## Affichage graphique
### 1. Emission par RunServer

    {...
	  "msg_type": "graphics"
	  "content": data #image à afficher 
	  	
     }

### 2. Retour par MrPython
   - variante 1 : succès

    ```
    {...
	"msg_type": "graphics_success"
	  "content": {
	               
				   "stdout" : str # sorties standard
				   "stderr" : str # sorties erreur
				   "report" : [ ... cf. "error" (mais que des warnings) ]
	             }
     }
    ```

   - variante 2 : erreur
   
    ```
    {...
	"msg_type": "graphics_error"
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
    ``` 
    

## Entrée sur console
### 1. Emission par RunServer

    {...
	  "msg_type": "input"
	   
     }

### 2. Retour par RunServer

    {...
	"msg_type": "input_return"
	"content": { 
			"chaine": str #chaine entrée sur la console
		   }	 
    }


	
