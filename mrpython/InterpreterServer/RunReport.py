


class ErrorReport:
    def __init__(self, severity, err_type, line, offset, details):
        self.severity = severity # 'info' 'warning' 'error'    (red, orange, red)
        self.err_type = err_type
        self.line = line
        self.offset = offset
        self.details = details

    def error_details(self):
        return "==> {}{}".format(self.err_type,
                                   ": {}".format(self.details) if self.details and self.details!=""
                                   else "")

    def __str__(self):
        s = ""
        if self.severity == 'warning':
            s = "{}{}".format("Warning",
                              ": line {}\n".format(self.line) if self.line else "")
            s = s + self.error_details()
        elif self.severity == 'error':
            s = "{}{}".format("Error",
                              ": line {}\n".format(self.line) if self.line else "")
            s = s + self.error_details()
        else:
            s = self.details

        return s


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

    def add_convention_error(self, severity, err_type, line=None, offset=None, details=""):
        self.convention_errors.append(ErrorReport(severity, err_type, line, offset, details))

    def add_compilation_error(self, severity, err_type, line=None, offset=None, details=""):
        self.compilation_errors.append(ErrorReport(severity, err_type, line, offset, details))

    def add_execution_error(self, severity, err_type, line=None, offset=None, details=""):
        self.execution_errors.append(ErrorReport(severity, err_type, line, offset, details))

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

