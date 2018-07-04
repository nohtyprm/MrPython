import sys
import glob

sys.path.append("../")

import mrpython.typechecking.prog_ast as prog_ast
import mrpython.typechecking.typechecker as typechecker


TESTPROG_PATH = "./progs"


def test_prog(prog_filename):
    pass

if __name__ == "__main__":

    for prog_file in glob.glob("{}/*.py".format(TESTPROG_PATH)):
        #print(prog_file)
        test_prog(prog_file)
