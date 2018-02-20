import unittest
from mrpython.typer import get_annotations, Type

class TestTypeChecking(unittest.TestCase):

    def test_get_annotations(self):
        correct_code ="""
# y : lolz
y = 123
# x : int
x = int
"""
        local_dict = get_annotations(correct_code)["__main__"]
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
        dict = get_annotations(code)
        print(dict)
        self.assertTrue(dict["first"]["x"].is_of("int"))
        self.assertTrue(dict["second"]["x"].is_of("float"))

if __name__ == '__main__':
    unittest.main()