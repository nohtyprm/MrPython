# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:54:59 2017

@author: 3605386
"""
import ast
from PSTL_MrPython_Client_Serveur.RunReport import RunReport
import sys
class Parser():
    #va parser
    def __init__(self):
        pass
    def parse(self,source,report,filename):
        try:
            res = ast.parse(source,filename)
            #print("je parse")
        #    # Handle the different kinds of compilation errors
        except IndentationError as err:
            report.add_compilation_error('error', "Bad indentation", err.lineno, err.offset)
            #print("indentationerror")
            #print(self.report.compilation_errors[0].error_details())
            return None,report
        except SyntaxError as err:
            report.add_compilation_error('error', "Syntax error", err.lineno, err.offset, details=err.text)
            #print("syntaxerror")
            #print(report.compilation_errors[0].error_details())
            return None,report
        except Exception as err:
            typ, exc, tb = sys.exc_info()
            report.add_compilation_error('error', str(typ), err.lineno, err.offset, details=str(err))
            #print(self.report.compilation_errors[0].error_details())
            return None,report
        return res,report
         
#f=open("test.txt")
#source=f.read()
#f.close()  
#r=RunReport()
       
#p=Parser(source,r,"test.txt")
#resu,r=p.parse()
#print(res)        