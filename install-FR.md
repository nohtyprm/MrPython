
Installation de MrPython
=========================

## Prérequis

Pour pouvoir utiliser MrPython, il est nécessaire de disposer d'un ordinateur avec :

 - un **système d'exploitation récent**, au choix :  Windows, MacOS X ou Linux (et autres systèmes Unix)

 - l'environnement Python dans une version supérieure ou égale à la 3.6, cf. https://www.python.org/downloads/

Des procédures d'installation plus détaillées sont données ci-dessous.

## Installation sous Windows (installateur)

Sous **Windows 10** le plus simple pour installer MrPython est d'utiliser
l'installateur dédié/

 - [Installateur pour MrPython v4.0.1](https://github.com/nohtyprm/MrPython/blob/win-installer/mrpython_4_0_1_install_FR.exe)
 
## Installation sous Windows (installation manuelle)
 
Il est aussi possible, sous windows, d'installer MrPython manuellement, voici les étapes principales :

### Etape 1 : installation de Python (si ce n'est déjà fait)

 - récupérer la dernière version stable de Python sur le site https://www.python.org
   - par exemple la version 3.8.5 : https://www.python.org/ftp/python/3.8.5/python-3.8.5.exe
   
 - procéder à l'installation
 
 ### Etape 2 : récupération des sources de MrPython
 
 - récupérer les sources de MrPython : https://github.com/nohtyprm/MrPython/archive/master.zip
 
 - extraire l'archive dans un répertoire de votre choix, cela créera un répertoire `MrPython-master\` avec
 les sources du logiciel.
 
Vous pouvez déjà tester l'installation en ouvrant l'explorateur Windows et en allant dans
le sous-répertoire `MrPython-master\mrpython\`  (donc `MrPython\mrpython\`),  vous pourrez double-cliquer sur le
fichier `Application.py` pour lancer MrPython.

### Etape 3 : création d'un lien (raccourcis) sur le bureau

Pour créer un lien (on parle aussi de raccourcis) dans le bureau, vous pouvez :

 - sélectionner le fichier `Application.py` (cf. étape précédente)

  - puis, tout en maintenant les touches `Shift` et `Control`, *glisser et déposer* l'icône dans le bureau.
  
Nous vous conseillons ensuite de renommer le raccourcis en `MrPython`, tout simplement. Normalement en double-cliquant
sur l'icône vous pourrez lancer MrPython.

## Installation sous MacOS (Installation manuelle)

Il n'y a pas encore d'installateur disponible pour MacOs, mais l'installation manuelle est assez simple,
 proche de celle de windows.

### Etape 1 : installation de Python (si ce n'est déjà fait)

La page [python.org](https://www.python.org/) propose un [installateur Python 3.8.6 pour MacOS](https://www.python.org/ftp/python/3.8.6/python-3.8.6-macosx10.9.pkg).
Vous pouvez alternativement installer Python (version 3.6 ou ultérieure) via [Momebrew](https://docs.brew.sh/Homebrew-and-Python) ou les [Macports](https://www.macports.org/), mais vous devez déjà connaître ces environnements.

### Etape 2 : récupération des sources de MrPython

 - récupérer les sources de MrPython : https://github.com/nohtyprm/MrPython/archive/master.zip
 
 - extraire l'archive dans un répertoire de votre choix, cela créera un répertoire `MrPython-master/` avec
 les sources du logiciel.

### Etape 3 : lancement de MrPython

Vous pouvez lancer MrPython en double-cliquant, dans le sous-répertoire `MrPython-master/mrpython/`, sur le fichier `Application.py`
Vous pouvez également utiliser le logiciel *Python Launcher* installé avec l'environnement Python sous Mac, en consultant
[la documentation associée](https://docs.python.org/fr/3/using/mac.html).


## Installation sous Linux (Ubuntu ou autre)

Pour disposer d'une version la plus à jour de MrPython, le plus simple est d'utiliser Linux qui est l'environnement
dans lequel MrPython est développé. Il existe plusieurs distributions de Linux et nous expliquons la marche à suivre
pour la distribution [Ubuntu](https://ubuntu.com/) dans ce qui suit. Cependant, il est en général assez facile
de traduire les explications pour les autres distributions de Linux.

### Etape 1 : installation de Python (si ce n'est déjà fait)

L'installation peut se faire, dans le terminal en mode administrateur, avec la commande suivante :

```shell
apt-get install python3.8 python3-tk 
```
(ici, par exemple, pour installer Python 3.8)

**Remarque** : sous Linux, contrairement aux autres systèmes, il est nécessaire d'installer la bibliothèque
d'interface graphique [tkinter](https://docs.python.org/fr/3/library/tkinter.html) (paquet `python3-tk`) séparément.

On peut directement passer directement en mode administrateur :

```shell
sudo apt-get install python3.8 python3-tk
```
(il faudra alors au préalable saisir le mot de passe administrateur)
 
### Etape 2 : récupération des sources de MrPython

 - récupérer les sources de MrPython : https://github.com/nohtyprm/MrPython/archive/master.zip
 
 - extraire l'archive dans un répertoire de votre choix, cela créera un répertoire `MrPython-master/` avec
 les sources du logiciel.
 
### Etape 3 : lancement de MrPython

Dans le terminal, vous pouvez aller dans le sous-répertoire `MrPython-master/mrpython` du projet :

```shell
cd MrPython-master/mrpython
```

puis lancer lancer le programme `Application.py` avec l'interprète Python :

```shell
python3 ./Application.py
```

Vous pourrez ensuite créer un alias ou un raccourcis de Bureau en consultant la documentation
de Linux et Ubuntu.

Par exemple (dans votre `.bashrc`) :

```shell
alias mrpython="python3.8 <chemin de MrPython>/MrPython-master/mrpython/Application.py"
```
(ou il faut remplacer `<chemin de MrPython>` par le chemin d'installation utilisé lors
de l'étape 1).

Pour plus d'informations sur les alias : https://doc.ubuntu-fr.org/alias
