class Specification:
    """
    Represents the different parts of a specification :
    - the name of the function
    - the parameters types
    - the return type
    - the description # useless ?
    """

    def __init__(self, line, function_name):
        parameters, sep, returning = line.partition("->")
        self.return_type = returning.strip()
        self.parameters = parameters.split("*")
        self.parameters = map(str.strip, parameters.split("*")) 
        self.function_name = function_name

def strip(s):
    """ Remove the spaces in the beginning and end of string """
    return s.strip()
