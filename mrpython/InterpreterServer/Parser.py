# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:54:59 2017

@author: 3605386
"""
import ast
from InterpreterServer.RunReport import RunReport
import sys
class Parser():
    '''
    Parsing class
    '''
    #va parser
    def __init__(self):
        pass
    def parse(self, source, report, filename):
        '''
        Parse a source code string 
        returns an ast and a report
        '''
        try:
            res = ast.parse(source, filename)
        # Handle the different kinds of compilation errors
        except IndentationError as err:
            report.add_compilation_error('error', "Bad indentation", err.lineno, err.offset)
            return None, report
        except SyntaxError as err:
            report.add_compilation_error('error', "Syntax error",
                                         err.lineno, err.offset, details=err.text)
            return None, report
        except Exception as err:
            typ, exc, tb = sys.exc_info()
            report.add_compilation_error('error', str(typ),
                                         err.lineno, err.offset, details=str(err))
            return None, report
        return res, report
