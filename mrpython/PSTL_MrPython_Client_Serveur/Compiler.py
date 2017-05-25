'''
Created on 27 avr. 2017

@author: 3301202
'''

from py_compile import PyCompileError
from PSTL_MrPython_Client_Serveur.RunReport import RunReport
from PSTL_MrPython_Client_Serveur.Parser import Parser
class Compiler(object):
    '''
    Compilateur
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    
    def compile(self,ast,report,compil_type,filename):
        try:
            code = compile(ast,filename, compil_type)
        except SyntaxError as err:
            report.add_compilation_error('error', "Compile error", err.lineno, err.offset, details=err.text)
            print("compileerror")
            print(report.compilation_errors[0].error_details())
            return None,report
        except ValueError as err:
            report.add_compilation_error('error', "Compile error", err.lineno, err.offset, details=err.text)
            print("compileerror")
            print(report.compilation_errors[0].error_details())
            return None,report
        #TODO: ajouter les erreurs
        return code,report