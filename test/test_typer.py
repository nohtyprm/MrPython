import sys
import glob
import os.path

sys.path.append("../")

import mrpython.typechecking.prog_ast as prog_ast
import mrpython.typechecking.typechecker as typechecker

TESTPROG_PATH = "./progs"

nb_tests_pass = 0
nb_tests_fail = 0
nb_tests_abort = 0
nb_tests = 0

def testWithoutTypeError(prog_filename, prog_name, prog):
    global nb_tests_pass, nb_tests_fail

    #print(sys.modules.keys())
    ctx = prog.type_check()
    if ctx.type_errors:
        print("  ==> FAIL: some type error has been raised")
        #print(ctx.type_errors)
        nb_tests_fail+=1
    else:
        print("  ==> PASS")
        nb_tests_pass+=1

def testWithTypeError(prof_filename, prog_name, prog):
    global nb_tests_abort

    print("  ==> ABORT: type error verifier not yet implemented")
    nb_tests_abort += 1

def test_prog(prog_filename):
    global nb_tests

    prog_name = os.path.splitext(os.path.basename(prog_filename))[0]
    ok = prog_name.endswith('OK')
    print("* Testing: {} ({})".format(prog_name, "expecting success" if ok else "expecting type error"))

    prog = prog_ast.Program()
    #print(type(prog))
    prog.build_from_file(prog_filename)

    if ok:
        testWithoutTypeError(prog_filename, prog_name, prog)
    else:
        testWithTypeError(prog_filename, prog_name, prog)

    nb_tests+=1

    print("")


def percent(value, maxi):
    return int(100.0*value/maxi)

if __name__ == "__main__":

    for prog_file in glob.glob("{}/*.py".format(TESTPROG_PATH)):
        test_prog(prog_file)

    print("-----")
    print("Summary: {} test cases".format(nb_tests))
    print("  ==> {} passed ({} %)".format(nb_tests_pass, percent(nb_tests_pass, nb_tests)))
    print("  ==> {} failed ({} %)".format(nb_tests_fail, percent(nb_tests_fail, nb_tests)))
    print("  ==> {} unsupported ({} %)".format(nb_tests_abort, percent(nb_tests_abort, nb_tests)))
