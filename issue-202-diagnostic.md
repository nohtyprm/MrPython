# Issue #202 — Precondition failure causes endless execution

## Summary

Two independent defects in the precondition machinery of `mrpython/StudentRunner.py`.
Both make an exception escape from *inside* the `except AssertionError` handler of
`_exec_or_eval`, which kills the interpreter subprocess loop and leaves the GUI
waiting forever — the "endless execution" reported in the issue.

The interpreter runs in a separate process (`mrpython/PyInterpreter.py`). Its
`run_loop` does:

```python
def run_loop():
    command = comm.recv()
    if command == 'eval':
        expr = comm.recv()
        ok, report = interp.run_evaluation(expr)   # <-- raises
        comm.send((ok, report))                     # <-- never reached
    ...
    root.after(10, run_loop)                        # <-- never reached
```

Any exception escaping `run_evaluation` means no answer is ever sent back **and**
the loop is never rescheduled. The proxy in the main process keeps polling
(`RUN_POLL_DELAY`) against a permanently silent interpreter. Nothing times out,
nothing is reported: the session hangs.

## Defect 1 — `inspect.getsource()` on a string (the reported hang)

`_exec_or_eval` is used in two modes:

| caller | `code` argument |
| --- | --- |
| `run()` — full file | a compiled **code object** |
| `evaluate()` — interactive prompt | the raw **expression string** |

The precondition branch of the `AssertionError` handler did:

```python
source_code = inspect.getsource(code)
```

which works for a code object and raises for a string:

```
TypeError: module, class, method, function, traceback, frame, or code object
           was expected, got str
```

Since this happens inside an `except` block, the `TypeError` propagates out of
`_exec_or_eval` → `evaluate` → `run_evaluation` → `run_loop`, and the interpreter
is dead.

This is exactly the asymmetry described in the issue: `assert func(-1) == -1` in
the file works (exec mode), typing `func(-1)` at the prompt hangs (eval mode).

**Reproduction**

```python
def func(a:int) -> int:
    """
    Renvoie un nombre positif tel quel
    Precondition: a>=0
    """
    return a

assert func(1)==1
```

Run the file, then evaluate `func(-1)` in the console.

## Defect 2 — line-number rewriting corrupts nested calls

`FunctionDefVisitor` injected the precondition assertions and then did:

```python
line_diff = new_end_lineno - node.lineno
ast.increment_lineno(node, n=line_diff)
```

`new_end_lineno` is just the number of preconditions (1, most of the time), so
`line_diff` is `1 - node.lineno`. Every function **not** starting on line 1 has
its whole body shifted to a bogus line range. A function defined at line 8 gets
its body reported around line 1.

That single line is responsible for a cascade of symptoms:

* **Wrong / missing error line.** The reported call site came from
  `traceb[-2].lineno`, which now points anywhere.
* **Silently swallowed errors.** The report was only filled in when
  `lineno in preconditionsLineno`. With corrupted line numbers this test fails,
  the `AssertionError` is caught, *nothing* is reported, and the program appears
  to run fine. (This is why `01_precondition_distance_KO`, `_lettre_KO` and
  `_longueur_KO` reported "an error was expected (found none)".)
* **Second hang.** See below.

The `TODO` comment above `add_FunctionPreconditions` ("because of changes in
python 3.11+ dynamic compilation we cannot add precondition checking code in
this way") was chasing this symptom; the line numbers were being destroyed by
MrPython itself, not by CPython.

## Defect 3 — argument values reconstructed by parsing source text

The error message was built by string-scanning the caller's source line
(`parse_assertion_arg_values`), and the parameter names by walking **every**
`FunctionDef` of the file:

```python
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        for argg in node.args.args:
            arg_names.append(argg.arg)          # names of ALL functions
...
arg_values = parse_assertion_arg_values(func_name, code_tb)   # text of the call

if len(arg_names) <= len(arg_values):
    ...
else:
    raise ValueError("Precondition handling fails (wrong parameter/value, please report)")
```

Consequences:

* **The `a=a` message.** When `func_1` calls `func`, the caller line is
  `return func(b)`, so the printed "value" is the literal source text `b`,
  not the value `-1`.
* **The secondary hang.** As soon as a second function has preconditions,
  `arg_names` holds the parameters of *all* functions while `arg_values` holds
  those of one call, so the counts mismatch and the `raise ValueError` fires —
  inside the `except` handler, killing the interpreter again. If the line
  numbers are corrupted (defect 2) the function name isn't even found in the
  caller line, `parse_assertion_arg_values` returns `None`, and the failure is
  a `TypeError: object of type 'NoneType' has no len()`.

This matches the issue precisely: removing the preconditions from the *caller*
makes the error report work again.

## Fix

Commit `0a1c60a`, `mrpython/StudentRunner.py`.

1. **Carry the precondition in the assertion message.**
   The injected assert now uses `PRECONDITION_TAG + ast.unparse(precondition)`
   as its message. The reported text no longer depends on reading the file back
   or on line numbers, and it works identically in exec and eval mode.

2. **Read the argument values from the frame.**
   The precondition checks are the first statements of the function body, so
   when one fails the locals of the deepest traceback frame *are* the call
   arguments:

   ```python
   arg_names = code.co_varnames[:code.co_argcount + code.co_kwonlyargcount]
   ... repr(frame.f_locals.get(arg_name))
   ```

   Real values, no source parsing, correct for nested calls. `a = -1` instead of
   `a = a`.

3. **Drop the line-number rewriting.**
   `ast.increment_lineno` and the `ast.FunctionDef(...)` reconstruction are
   gone; the visitor now mutates `node.body` in place, which also preserves
   fields the reconstruction dropped (`type_params`, `end_lineno`,
   decorator positions).

4. **Never report a meaningless line.**
   The call site is reported only when the frame belongs to the edited file, so
   an interactive `func(-1)` no longer points at an unrelated line of the file.

5. **Remove the swallow path.**
   `preconditionsLineno` and `parse_assertion_arg_values` are deleted. Nothing
   can escape the handler, and a precondition failure is always reported.

Also fixed in `runtimeTest/test_runtime.py`: test programs were read with
`open(f, "r")`, i.e. the platform default encoding. On Windows (cp1252) the
accented `Précondition` was mis-decoded and never recognised, so four tests were
failing for that reason alone. Now read with `tokenize.open`, like the
application itself does.

## Result

Interactive evaluation, previously an infinite hang:

```
>>> func(-1)
Erreur de précondition
     Fonction : func (Ligne 4)
     Précondition : a >= 0
     Fausse avec
        a = -1
```

Nested case (`petit_positif` calls `positif`, both with preconditions),
previously an infinite hang:

```
Erreur: ligne 13
==> Erreur de précondition
     Fonction : positif (Ligne 5)
     Précondition : a >= 0
     Fausse avec
        a = -1
```

Test suites:

| suite | before | after |
| --- | --- | --- |
| `runtimeTest/test_runtime.py` | 20 / 24 | **26 / 26** |
| `test/test_typer.py` | 113 / 118 | 113 / 118 (unchanged) |

Two regression programs were added, `01_precondition_nested_OK.py` and
`01_precondition_nested_KO.py`, covering a preconditioned function called from
another preconditioned function.

The 5 remaining `test_typer.py` failures are pre-existing and unrelated to
preconditions.

## Left aside

`mrpython/PreconditionHandler.py` still contains `PreconditionErrorMessageHandler`,
dead code carrying the same broken source-parsing approach (and a call to an
undefined `tr`). It is unused and can be deleted separately.
