'''
Created on 28 avr. 2017

@author: 3301202
'''

class Reporter(object):
    '''
    Transforms a run report into a dictionary that can be serialized in json
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def compute_report(self, report):
        '''
        Transforms a run report into a dictionary that can be serialized in json
        '''

        list_report = []
        for i in report.convention_errors:
            dict_temp = {}
            dict_temp["error_type"] = "student"
            dict_temp["traceback"] = None
            dict_temp["infos"] = {"student_error_type":"convention",
                                  "severity" : i.severity,
                                  "description" : i.error_details(),
                                  "lines" : i.line}
            list_report.append(dict_temp)

        for i in report.compilation_errors:
            dict_temp = {}
            dict_temp["error_type"] = "compilation"
            dict_temp["traceback"] = None
            dict_temp["infos"] = {"student_error_type":"compilation",
                                  "severity" : i.severity,
                                  "description":i.error_details(),
                                  "lines":i.line}
            list_report.append(dict_temp)

        for i in report.execution_errors:
            dict_temp = {}
            dict_temp["error_type"] = "execution"
            dict_temp["traceback"] = None
            dict_temp["infos"] = {"student_error_type":"execution",
                                  "severity" : i.severity,
                                  "description":i.error_details(),
                                  "lines":i.line}
            list_report.append(dict_temp)
        res = {}
        res["header"] = report.header
        res["footer"] = report.footer
        res["errors"] = list_report
        return res
        