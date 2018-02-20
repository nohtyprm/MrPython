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

if __name__ == '__main__':
    unittest.main()