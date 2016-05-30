class RunReport:
    """
    Handles the result of the execution of the source code
    """
    
    def __init__(self):
        # These attributes are for the student mode checkings
        # Format of the convention_errors list :
        # [[ 'type_err1', details1 ], [ 'type_err2', details2 ]]
        self.convention_errors = []
        # These attributes are for the compilation errors
        self.compilation_errors = []
        # These attributes are for the execution errors
        self.execution_errors = []
        # Result of the execution
        self.result = None


    def asserts_not_valid(self, details=None):
        """ Method called when the asserts test has failed """
        self.convention_errors.append(['asserts'])


    def specifications_not_valid(self, details=None):
        """ Method called when the function specification test has failed """
        self.convention_errors.append(['specifications'])


    def add_compile_error(self, err_type, line, offset, details=None):
        """ If there is a compilation error, put the details of it at the end of
            the list """
        if details == None:
            self.compilation_errors.extend([err_type, line, offset])
        else:
            self.compilation_errors.extend([err_type, line, offset, details])


    def add_execution_error(self, err_type, line, details=None):
        """ If an execution error occured, add it at the end of the execution
            errors list """
        if details is None:
            self.execution_errors.extend([err_type, line])
        else:
            self.execution_errors.extend([err_type, line, details])


    def set_result(self, result):
        """ Set the result of the execution : no error occured """
        self.result = result


