import unittest
from mrpython.typechecking.typer import get_annotations, Type

class TestTypeChecking(unittest.TestCase):

    def test_get_annotations(self):
        correct_code ="""
# y : lolz
y = 123
# x : int
x = int
"""
        local_dict = get_annotations(correct_code)[0]["__main__"]
        self.assertTrue(local_dict['y'].class_eq(Type("lolz", 2)))
        self.assertEqual(local_dict['x'], Type('int', 4))

    def test_function_env(self):
        code = """
def first():
    # x : int
    x = 3

def second():
    # x : float
    x = 3.0
"""
        dict = get_annotations(code)[0]
        print(dict)
        self.assertTrue(dict["first"]["x"].is_of("int"))
        self.assertTrue(dict["second"]["x"].is_of("float"))

    def test_warning_no_annot(self):
        code = """
# x : int
x = 2
y = x + 2
"""
        warnings = get_annotations(code)[1]


if __name__ == '__main__':
    unittest.main()