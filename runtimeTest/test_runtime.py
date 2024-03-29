import sys
import glob
import os.path

sys.path.append("../mrpython")

import typechecking.prog_ast as prog_ast
import typechecking.typechecker as typechecker
import StudentRunner as studentRunner

TESTPROG_PATH = "./progs"

nb_tests_pass = 0
nb_tests_fail = 0
nb_tests_abort = 0
nb_tests = 0

def testWithoutPreconditionError(prog_filename, prog_name, prog):
    global nb_tests_pass, nb_tests_fail

    ctx = prog.type_check()
    if ctx.type_errors:
        print("  ==> FAIL: some type error has been raised")
        for error in ctx.type_errors:
            print("      | " + error.fail_string())
        nb_tests_fail+=1
    else:
        runner = studentRunner.StudentRunner(None, prog_filename,open(prog_filename,"r").read(), check_tk=False)
        runner.execute(dict(), capture_stdout=False)
        if runner.report.has_execution_error():
            print("  ==> FAIL: precondition error has been raised")
            nb_tests_fail+=1
        else:
            print("  ==> PASS: no precondition error")
            nb_tests_pass+=1

def testWithPreconditionError(prog_filename, prog_name, prog):
    global nb_tests_abort, nb_tests_fail, nb_tests_pass
    with open(prog_filename, 'r') as f:
        header = f.readline()

    if not header.startswith("##!FAIL:"):
        print("  ==> ABORT: the test file does not begin with the ##!FAIL: string")
        nb_tests_abort += 1
        return
    
    ctx = prog.type_check()
    if ctx.type_errors:
        print("  ==> FAIL: some type error has been raised")
        for error in ctx.type_errors:
            print("      | " + error.fail_string())
        nb_tests_fail+=1
    runner = studentRunner.StudentRunner(None, prog_filename,open(prog_filename,"r").read(), check_tk=False)
    runner.execute(dict(), capture_stdout=False)
    if not runner.report.has_execution_error():
        print("  ==> FAIL: an error was expected (found none)")
        nb_tests_fail += 1
        return
    valid_string = header[8:].strip()
    computed_string =  runner.report.execution_errors[0].__str__().splitlines()[0].strip()
    print(computed_string)
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
    print("* Testing: {} ({})".format(prog_name, "expecting success" if ok else "expecting precondition error"))

    prog = prog_ast.Program()
    prog.build_from_file(prog_filename)

    if ok:
        testWithoutPreconditionError(prog_filename, prog_name, prog)
    else:
        testWithPreconditionError(prog_filename, prog_name, prog)

    nb_tests+=1

    print("")


def percent(value, maxi):
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
