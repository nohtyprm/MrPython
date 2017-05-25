'''
Created on 28 avr. 2017

@author: 3301202
'''

class Reporter(object):
    '''
    Modifie un rapport pour le transformer en dictionnaire json-serializable
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def compute_report(self, report):
        
        list_report =[]
        for i in report.convention_errors:
            dict_temp = {}
            dict_temp["error_type"] = "student"
            dict_temp["traceback"] = None #Si necessaire l'ajouter au RunReport
            dict_temp["infos"] = {"student_error_type":"convention",
                                    "severity" : i.severity,
                                    "description":i.error_details(),
                                    "lines":i.line} # Il manque les lignes?
            list_report.append(dict_temp)

        for i in report.compilation_errors:
            dict_temp = {}
            dict_temp["error_type"] = "compilation"
            dict_temp["traceback"] = None #Si necessaire l'ajouter au RunReport
            dict_temp["infos"] = {"student_error_type":"compilation",
                                    "severity" : i.severity,
                                    "description":i.error_details(),
                                    "lines":i.line} # Il manque les lignes?
            list_report.append(dict_temp)

        for i in report.execution_errors:
            dict_temp = {}
            dict_temp["error_type"] = "execution"
            dict_temp["traceback"] = None #Si necessaire l'ajouter au RunReport
            dict_temp["infos"] = {"student_error_type":"execution",
                                     "severity" : i.severity,
                                    "description":i.error_details(),
                                    "lines":i.line} # Il manque les lignes?
            list_report.append(dict_temp)
        res={}
        res["header"]=report.header
        res["footer"]=report.footer
        res["errors"]=list_report
        return res
        


        