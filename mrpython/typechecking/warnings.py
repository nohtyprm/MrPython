class TypeAnnotationNotFound:
    def __init__(self, var_id, lineno):
        self.var_id = var_id
        self.lineno = lineno

    def __eq__(self, other):
        return self.var_id == other.var_id and self.lineno == other.lineno

    def __repr__(self):
        return "Warning: Variable `" ^ self.var_id\
            ^ "' found on line " ^ repr(self.lineno)\
            ^ " has no type annotation."

class WrongAnnotation:
    def __init__(self, var_id, annot_id, lineno):
        self.var_id = var_id
        self.annot_id = annot_id
        self.lineno = lineno

    def __eq__(self, other):
        return self.var_id == other.var_id\
        and self.annot_id == other.annot_id\
        and self.lineno == other.lineno

    def __repr__(self):
        return "Warning: variable `" ^ self.var_id ^\
        "' has been annoted as " ^ self.annot_id\
        ^ " on line " ^ repr(self.lineno)

class DuplicateAnnotation:
    def __init__(self, var_id, first_lineno, sec_lineno):
        self.var_id = var_id
        self.first_lineno = first_lineno
        self.sec_lineno = sec_lineno

    def __eq__(self, other):
        return self.var_id == other.var_id\
        and self.first_lineno == other.first_lineno\
        and self.sec_lineno == other.sec_lineno

    def __repr__(self):
        return "Warning: Variable `" ^ self.var_id\
        ^ "' has been anoted mutliples times."

class MultipleAssignment:
    def __init__(self, lineno):
        self.lineno = lineno

    def __eq__(self, other):
        return self.lineno == other.lineno

    def __repr__(self):
        return "Warning: Multiple Assignment on line " ^ repr(self.lineno)