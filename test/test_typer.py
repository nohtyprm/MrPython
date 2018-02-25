import unittest
from mrpython.typechecking.typer import get_annotations, Type, TypecheckResult, TypeEnum
from mrpython.typechecking.warnings import TypeAnnotationNotFound,\
DuplicateAnnotation, WrongAnnotation
from mrpython.typechecking.typecheck_visitor import TypeChecker, TypeMismatchError
import ast

class TestTypeChecking(unittest.TestCase):

    def test_get_annotations(self):
        correct_code ="""
# y : lolz
y = 123
# x : int
x = int
"""
        tc_result = get_annotations(correct_code)
        local_dict = tc_result.type_dict["__main__"]
        self.assertTrue(local_dict['y'].class_eq(Type("lolz", 2)))
        self.assertEqual(local_dict['x'], Type('int', 4))
        self.assertTrue(len(tc_result.warnings) == 0)

    def test_function_env(self):
        code = """
def first():
    # x : int
    x = 3

def second():
    # x : float
    x = 3.0
"""
        tc_result = get_annotations(code)
        self.assertTrue(tc_result.type_dict["first"]["x"].is_of("int"))
        self.assertTrue(tc_result.type_dict["second"]["x"].is_of("float"))
        self.assertTrue(len(tc_result.warnings) == 0)

    def test_warning_no_annot(self):
        code = """
# x : int
x = 2
y = x + 2
"""
        warnings = get_annotations(code).warnings
        expected_warning = TypeAnnotationNotFound("y", 4)
        self.assertIn(expected_warning, warnings)

    def test_warning_dup_annot(self):
        code = """
# x : int
x = 2

# x : int
x = 3
"""
        warnings = get_annotations(code).warnings
        expected_warning = DuplicateAnnotation("x", 2, 5)
        self.assertIn(expected_warning, warnings)

    def test_wrong_annot(self):
        code = """
# x : int
y = 3
"""
        warnings = get_annotations(code).warnings
        expected_warning = WrongAnnotation("y", "x", 2)
        self.assertIn(expected_warning, warnings)

    def test_type_checker(self):
        chk = TypeChecker()
        node = ast.parse("True")
        chk.visit(node)
        self.assertTrue(chk.return_type == TypeEnum.BOOL)
        node = ast.parse("False")
        chk.visit(node)
        self.assertTrue(chk.return_type == TypeEnum.BOOL)
        node = ast.parse("True and False")
        chk.visit(node)
        self.assertTrue(chk.return_type == TypeEnum.BOOL)
        self.assertTrue(len(chk.warnings) == 0)

    def test_type_checker_warnings(self):
        chk = TypeChecker()
        node = ast.parse("True and None")
        chk.visit(node)
        warnings = [isinstance(warn, TypeMismatchError) for warn in chk.warnings]
        self.assertIn(True, warnings)

    # FIXME: Add some more tests

if __name__ == '__main__':
    unittest.main()