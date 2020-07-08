
from translate import tr

class ErrorReport:
    def __init__(self, severity, err_type, line, offset, details, class_name):  # Added class_name for tracing
        self.severity = severity # 'info' 'warning' 'error'    (red, orange, red)
        self.err_type = err_type
        self.line = line
        self.offset = offset
        self.details = details
        self.class_name = class_name

    def error_details(self):
        return "==> {}{}".format(self.err_type,
                                   ": {}".format(self.details) if self.details and self.details!=""
                                   else "")

    def __str__(self):
        s = ""
        if self.severity == 'warning':
            s = "{}{}".format(tr("Warning"),
                              tr(": line {}\n").format(self.line) if self.line else "")
            s = s + self.error_details()
        elif self.severity == 'error':
            s = "{}{}".format(tr("Error"),
                              tr(": line {}\n").format(self.line) if self.line else "")
            s = s + self.error_details()
        else:
            s = self.details

        return s

    def __repr__(self):
        return str(self)


class RunReport:
    """
    Handles the result of the execution of the source code
    """

    def __init__(self):

        self.convention_errors = []
        self.compilation_errors = []
        self.execution_errors = []

        self.result = None
        self.output = ""

        self.header = ""
        self.footer = ""

        self.nb_passed_tests = 0


    def add_convention_error(self, severity, err_type, line=None, offset=None, details="", class_name = ""):
        self.convention_errors.append(ErrorReport(severity, err_type, line, offset, details, class_name))

    def has_convention_error(self):
        return bool(self.convention_errors)
        
    def add_compilation_error(self, severity, err_type, line=None, offset=None, details="", class_name = ""):
        self.compilation_errors.append(ErrorReport(severity, err_type, line, offset, details, class_name))

    def has_compilation_error(self):
        return bool(self.compilation_errors)

    def add_execution_error(self, severity, err_type, line=None, offset=None, details="", class_name = ""):
        self.execution_errors.append(ErrorReport(severity, err_type, line, offset, details, class_name))

    def has_execution_error(self):
        return bool(self.execution_errors)
        
    def set_output(self, output):
        """Set the (standard) output of an execution."""
        self.output = output

    def set_result(self, result):
        """ Set the result of the execution : no error occured """
        self.result = result

    def set_header(self, header):
        self.header = header

    def set_footer(self, footer):
        self.footer = footer

    def __str__(self):
        return """
Report:
 ==> convention errors = {}
 ==> compilation errors = {}
 ==> execution errors = {}
 ==> output = {}
""".format(self.convention_errors,
           self.compilation_errors,
           self.execution_errors,
           self.output)

