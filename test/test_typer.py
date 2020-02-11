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
        for error in ctx.type_errors:
            print("      | " + error.fail_string())
        nb_tests_fail+=1
    else:
        print("  ==> PASS: no type error")
        nb_tests_pass+=1

def testWithTypeError(prog_filename, prog_name, prog):
    global nb_tests_abort, nb_tests_fail, nb_tests_pass

    with open(prog_filename, 'r') as f:
        header = f.readline()
    #print(header)

    if not header.startswith("##!FAIL:"):
        print("  ==> ABORT: the test file does not begin with the ##!FAIL: string")
        nb_tests_abort += 1
        return

    ctx = prog.type_check()
    if not ctx.type_errors:
        print("  ==> FAIL: an error was expected (found none)")
        nb_tests_fail += 1
        return

    valid_string = header[8:].strip()
    #print(valid_string)

    computed_string = ctx.type_errors[0].fail_string()

    if computed_string != valid_string:
        print("  ==> FAIL: mismatch error, expecting: {}".format(valid_string))
        print("          | computed = {}".format(computed_string))
        nb_tests_fail += 1
    else:
        print("  ==> PASS: {}".format(valid_string))
        nb_tests_pass += 1

def test_prog(prog_filename):
    global nb_tests

    prog_name = os.path.splitext(os.path.basename(prog_filename))[0]
    ok = (prog_name.find('OK') != -1)
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
    if maxi == 0:
        return 0
    return int(100.0*value/maxi)

if __name__ == "__main__":

    if sys.argv[1:]:
        prog_files = sys.argv[1:]
    else:
        prog_files = glob.glob("{}/*.py".format(TESTPROG_PATH))

    for prog_file in prog_files:
        test_prog(prog_file)

    print("-----")
    print("Summary: {} test cases".format(nb_tests))
    print("  ==> {} passed ({} %)".format(nb_tests_pass, percent(nb_tests_pass, nb_tests)))
    print("  ==> {} failed ({} %)".format(nb_tests_fail, percent(nb_tests_fail, nb_tests)))
    print("  ==> {} unsupported ({} %)".format(nb_tests_abort, percent(nb_tests_abort, nb_tests)))
