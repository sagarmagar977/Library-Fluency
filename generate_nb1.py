"""
Generates 01_Python_Execution_Core_Runtime_Lab.ipynb
"""
from build_notebook_helper import make_notebook, md_cell, code_cell, validate_and_save

cells = [
    md_cell("""# 01 — Python Execution & Core Runtime Laboratory

## 0. Notebook Overview

* **Chapter Correlation**: Chapter 1 — Python Execution & Core Runtime
* **Purpose**: Provide an executable, observable experimental environment to inspect CPython's execution model, object memory model, scoping rules, closure cells, and dynamic stack frames.
* **Prerequisites**: Working knowledge of basic Python syntax and function definitions.
* **Python Version**: Python 3.10+ (tested on Python 3.14).
* **Required Libraries**: Standard library only (`dis`, `sys`, `ast`, `copy`, `functools`, `types`).
* **Source Attribution Policy**:
  * `[SOURCE-DERIVED]`: Adapted from core concepts in *Fluent Python (2nd Ed)* and *Python Distilled*.
  * `[SOURCE-ADAPTED]`: Simplified and condensed recipes from *Python Cookbook (3rd Ed)* and *Effective Python*.
  * `[ORIGINAL LAB EXPERIMENT]`: Targeted runtime inspection and dissection scripts developed for this laboratory.
"""),

    md_cell("""## 1. Mental Model Map

```text
Source Code Text (my_script.py)
       │
       ▼ (Parser)
Abstract Syntax Tree (ast.AST)
       │
       ▼ (Compiler)
Immutable Code Object (PyCodeObject: co_code, co_consts, co_varnames)
       │
       ▼ (Evaluation Frame Allocation)
Dynamic Execution Frame (PyFrameObject: f_locals, f_globals, f_builtins, f_back, f_lasti)
       │
       ▼ (Interpreter Loop)
Bytecode Evaluation Stack (Pushes / Pops Object References)
```
"""),

    md_cell("""---
## 2. Core Runtime Experiments
"""),

    # Experiment 1.1
    md_cell("""### Experiment 1.1 — The CPython Compilation Pipeline
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
We trace how Python source code string is parsed into an Abstract Syntax Tree (AST), compiled into an immutable `PyCodeObject`, and evaluated inside a dynamic `PyFrameObject`.

#### Mental Model
Code objects (`PyCodeObject`) store purely static bytecode instructions, constant values, and variable name tuples. They contain **zero** runtime values or variable bindings. Execution frames (`PyFrameObject`) are created dynamically at function call time to provide memory slots (`f_locals`, `f_globals`) for variable evaluation.

#### Code
We parse a code snippet into an AST, compile it into a code object, and inspect its internal tables.

#### Predict Before Running
Will the compiled code object contain the value of `x` (i.e. `42`), or only the variable name `'x'` and the constant literal `42` stored separately?
"""),

    code_cell("""import ast
import dis

source_code = \"\"\"
def compute(x):
    y = x * 2 + 10
    return y
\"\"\"

# 1. Parse into Abstract Syntax Tree
parsed_ast = ast.parse(source_code)
print("AST Root:", type(parsed_ast).__name__)

# 2. Compile into Code Object
code_obj = compile(parsed_ast, filename="<lab>", mode="exec")
print("Compiled Object Type:", type(code_obj).__name__)

# 3. Extract the function's nested code object
func_code = [c for c in code_obj.co_consts if hasattr(c, "co_code")][0]
print("Function Name:", func_code.co_name)
print("co_varnames (Local names):", func_code.co_varnames)
print("co_consts (Literals):", func_code.co_consts)
"""),

    md_cell("""#### Observe
The function code object (`func_code`) holds variable names `('x', 'y')` in `co_varnames` and constants `(None, 2, 10)` in `co_consts`. It contains no runtime state.

#### Inspect
We disassemble the function bytecode using `dis.dis()` to see the exact stack operations:
"""),

    code_cell("""dis.dis(func_code)"""),

    md_cell("""#### Explain
Notice the opcodes:
- `LOAD_FAST 0 (x)`: Pushes parameter `x` from the fast local array slot onto the evaluation stack.
- `LOAD_CONST 1 (2)`: Pushes constant `2`.
- `BINARY_OP / BINARY_MULTIPLY`: Pops top two items, multiplies, pushes result.
- `LOAD_CONST 2 (10)`: Pushes constant `10`.
- `BINARY_OP / BINARY_ADD`: Pops and adds.
- `STORE_FAST 1 (y)`: Stores top of stack into local slot 1 (`y`).
- `LOAD_FAST 1 (y)`: Pushes `y`.
- `RETURN_VALUE`: Returns the top of stack to caller frame.

#### Modify
Change `y = x * 2 + 10` to `y = x * 2 + z` where `z` is not defined locally. Re-run and observe that `z` moves to `co_names` (global lookup) rather than `co_varnames` (local lookup)!

#### Recall Rule
> **Code objects (`PyCodeObject`) store static bytecode and symbol tables; frame objects (`PyFrameObject`) manage dynamic runtime namespaces.**
"""),

    # Experiment 1.2
    md_cell("""---
### Experiment 1.2 — Object Identity, Names & Reference Assignment
*Category: [SOURCE-DERIVED - Fluent Python Ch 1]*

#### What are we investigating?
We verify that Python variables are names bound to object references, not memory boxes holding values. Assignment (`=`) never copies data.

#### Mental Model
```text
Binding (a = b):
[ a ] ───┐
         ▼
       [ Object in Memory ] (id: 0x7fa... / type: list / value: [1, 2])
         ▲
[ b ] ───┘
```

#### Code
We create a list, bind multiple names to it, and compare `id()`, `is`, and equality `==`.

#### Predict Before Running
If `b = a` and we mutate `b.append(3)`, will `id(a)` change? Will `a` reflect the added element?
"""),

    code_cell("""a = [1, 2]
b = a
c = [1, 2]

print(f"id(a): {id(a)}, id(b): {id(b)}, id(c): {id(c)}")
print(f"a is b: {a is b} (Same object identity)")
print(f"a is c: {a is c} (Distinct objects with equal values)")
print(f"a == c: {a == c} (Values match)")

# Mutate via b
b.append(3)
print(f"After b.append(3) -> a: {a}, b: {b}")
print(f"a is b still: {a is b}")
"""),

    md_cell("""#### Observe
`a is b` evaluates to `True` because both identifiers point to the identical heap address. Mutating `b` immediately affects `a`. `c` has the same values but a distinct `id`.

#### Inspect
Use `id()` and `hex(id())` to inspect the raw memory pointer:
"""),

    code_cell("""print("Pointer hex(id(a)):", hex(id(a)))
print("Pointer hex(id(b)):", hex(id(b)))
print("Pointer hex(id(c)):", hex(id(c)))"""),

    md_cell("""#### Explain
In CPython, `id(obj)` is the actual virtual memory address of the underlying `PyObject` structure. Assignment (`=`) increments the object's internal reference count and binds the name in the current frame's namespace dictionary.

#### Recall Rule
> **Assignment binds an identifier name; it never copies object data.**
"""),

    # Experiment 1.3
    md_cell("""---
### Experiment 1.3 — Mutability Traps: The Mutating Tuple Anomaly
*Category: [SOURCE-DERIVED - Fluent Python Ch 1]*

#### What are we investigating?
We observe the infamous CPython augmented assignment anomaly: modifying a mutable object located inside an immutable tuple.

#### Mental Model
A `tuple` is immutable in that its array of references cannot be rebound. However, the objects referenced by those slots may themselves be mutable! When `+=` is executed on a tuple item, `__iadd__` succeeds in-place, but the subsequent tuple item assignment fails.

#### Code
We place a list inside a tuple, attempt `t[0] += [3]`, and capture the resulting exception.

#### Predict Before Running
Will `t[0] += [3]` fail with `TypeError`? If it fails, will `t[0]` contain `[1, 2]` or `[1, 2, 3]`?
"""),

    code_cell("""t = ([1, 2], "immutable")

print("Before:", t)
try:
    # Attempt augmented assignment on tuple element
    t[0] += [3]
except TypeError as err:
    print("Caught Exception:", type(err).__name__, "-", err)

print("After:", t)
"""),

    md_cell("""#### Observe
The operation raised `TypeError: 'tuple' object does not support item assignment`, yet the list inside `t[0]` **was mutated** to `[1, 2, 3]`!

#### Inspect
Disassemble the operation to understand why this happens:
"""),

    code_cell("""code = compile("t[0] += [3]", "<test>", "exec")
dis.dis(code)"""),

    md_cell("""#### Explain
Look at the bytecode sequence:
1. `BINARY_OP 13 (+=)` calls `list.__iadd__`, mutating the list in-place and returning its reference.
2. `STORE_SUBSCR` attempts to assign that returned reference back to `t[0]`.
3. Because `t` is a tuple, `tuple.__setitem__` raises `TypeError`.
The in-place mutation already completed before the assignment check failed!

#### Recall Rule
> **Avoid placing mutable objects inside immutable containers if you plan to perform augmented assignments.**
"""),

    # Experiment 1.4
    md_cell("""---
### Experiment 1.4 — Shallow Copy vs Deep Copy
*Category: [SOURCE-ADAPTED - Python Distilled Ch 3]*

#### What are we investigating?
We compare identity and reference behavior across reference binding (`=`), shallow copying (`copy.copy()`), and deep copying (`copy.deepcopy()`).

#### Mental Model
```text
Shallow Copy:
[ New Outer Container ] ──> points to ORIGINAL nested objects
Deep Copy:
[ New Outer Container ] ──> points to NEW RECURSIVELY COPIED nested objects
```

#### Code
We create a nested list structure and copy it using both methods.

#### Predict Before Running
If we mutate a nested list inside a shallow copy, will the original outer object reflect the change? What if we mutate a nested list inside a deep copy?
"""),

    code_cell("""import copy

original = [[10, 20], [30, 40]]

shallow = copy.copy(original)
deep = copy.deepcopy(original)

print("original is shallow:", original is shallow)
print("original[0] is shallow[0]:", original[0] is shallow[0], "(Shared reference!)")
print("original[0] is deep[0]:", original[0] is deep[0], "(Independent copy!)")

# Mutate nested element in shallow copy
shallow[0].append(999)
print("\\nAfter shallow[0].append(999):")
print("original:", original)
print("shallow: ", shallow)
print("deep:    ", deep)
"""),

    md_cell("""#### Observe
`original[0]` was modified when `shallow[0]` was appended because shallow copy duplicates only the outer list container, retaining references to the same inner lists. `deep` remained completely untouched.

#### Inspect
Inspect identities of inner objects:
"""),

    code_cell("""print(f"ID original[0]: {id(original[0])}")
print(f"ID shallow[0]:  {id(shallow[0])}")
print(f"ID deep[0]:     {id(deep[0])}")"""),

    md_cell("""#### Recall Rule
> **Shallow copy creates a new container with existing element references; deep copy recursively copies the entire object graph.**
"""),

    # Experiment 1.5
    md_cell("""---
### Experiment 1.5 — LEGB Scope Hierarchy & The `UnboundLocalError` Trap
*Category: [SOURCE-DERIVED - Fluent Python Ch 7]*

#### What are we investigating?
We demonstrate how CPython determines variable scope at compile time based on assignment syntax, leading to `UnboundLocalError`.

#### Mental Model
When Python compiles a function body, any variable that is assigned to (`x = ...`) anywhere within that function is marked as a **local variable** for the entire function scope. Global lookup is blocked unless explicitly declared with `global x`.

#### Code
We define a global `val = 100`, read `val`, and then assign `val = 200` later in the same function.

#### Predict Before Running
Will the function print `100` and then rebind `val` locally to `200`, or will it raise an error on the print statement?
"""),

    code_cell("""val = 100

def broken_scope():
    print("Reading val:", val)  # What happens here?
    val = 200                   # Local assignment!

try:
    broken_scope()
except UnboundLocalError as e:
    print("Caught Error:", type(e).__name__, "-", e)
"""),

    md_cell("""#### Observe
Python raises `UnboundLocalError: cannot access local variable 'val' where it is not associated with a value`.

#### Inspect
Inspect the compiled code object's symbol tables:
"""),

    code_cell("""print("broken_scope co_varnames:", broken_scope.__code__.co_varnames)
print("broken_scope co_names (globals):", broken_scope.__code__.co_names)"""),

    md_cell("""#### Explain
Because `val = 200` appears inside `broken_scope`, the compiler added `'val'` to `co_varnames`. At line 1, Python emits `LOAD_FAST 0 (val)`. Since slot 0 has not yet been initialized, CPython immediately raises `UnboundLocalError`.

To fix this:
- Use `global val` if intending to modify module global state.
- Or assign to a distinct local variable name (e.g. `new_val = val + 100`).

#### Recall Rule
> **Scope is determined at compile time by assignment syntax, not at runtime by execution order.**
"""),

    # Experiment 1.6
    md_cell("""---
### Experiment 1.6 — Closures, Free Variables & Cell Objects
*Category: [SOURCE-DERIVED - Python Distilled Ch 4]*

#### What are we investigating?
We inspect how closures preserve state across function calls using heap-allocated `cell` objects, and dissect the infamous late-binding loop variable bug.

#### Mental Model
A closure occurs when an inner function references an identifier in an enclosing function scope. CPython stores the shared reference inside a heap-allocated **cell object** (`PyCellObject`). The inner function references this cell via `__closure__`.

#### Code
We create a classic closure and inspect its cell contents. Then we demonstrate the loop late-binding bug.

#### Predict Before Running
In `funcs = [lambda: i for i in range(3)]`, what will `[f() for f in funcs]` return: `[0, 1, 2]` or `[2, 2, 2]`?
"""),

    code_cell("""def make_counter(start=0):
    count = start
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter(10)
print("Call 1:", counter())
print("Call 2:", counter())

# Inspect the closure cell
print("\\nClosure Tuple:", counter.__closure__)
cell = counter.__closure__[0]
print("Cell Object:", type(cell))
print("Live Cell Contents:", cell.cell_contents)
"""),

    md_cell("""Now observe the loop late-binding bug:
"""),

    code_cell("""# Buggy late-binding loop
buggy_funcs = [lambda: i for i in range(3)]
print("Buggy result:", [f() for f in buggy_funcs])

# Inspect closure cells for all 3 lambdas
for idx, f in enumerate(buggy_funcs):
    print(f"Lambda {idx} cell pointer: {id(f.__closure__[0])}, contents: {f.__closure__[0].cell_contents}")
"""),

    md_cell("""#### Observe
All three lambdas point to the exact same cell object containing `2` (the final iteration value).

#### The Idiomatic Fix: Default Parameter Binding
We force evaluation at definition time by binding the loop variable to a default argument:
"""),

    code_cell("""fixed_funcs = [lambda i=i: i for i in range(3)]
print("Fixed result:", [f() for f in fixed_funcs])
print("Fixed func closure (None because 'i' is now a local argument):", fixed_funcs[0].__closure__)
"""),

    md_cell("""#### Recall Rule
> **Closures bind to variable cells, not static value snapshots. Default arguments evaluate at function definition time.**
"""),

    # Experiment 1.7
    md_cell("""---
### Experiment 1.7 — Decorator Metadata Preservation with `functools.wraps`
*Category: [SOURCE-ADAPTED - Python Cookbook Ch 9]*

#### What are we investigating?
We demonstrate how decorators alter callable metadata (`__name__`, `__doc__`, `__wrapped__`) and how `@functools.wraps` preserves introspection integrity.

#### Mental Model
A decorator `func = dec(func)` wraps a function inside an outer wrapper. Without metadata copying, tools like `help()`, debuggers, and IDEs lose track of the underlying function.

#### Code
We build a decorator with and without `@functools.wraps`.
"""),

    code_cell("""import functools

def logging_dec(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        \"\"\"Wrapper docstring.\"\"\"
        return fn(*args, **kwargs)
    return wrapper

@logging_dec
def calculate_tax(amount: float) -> float:
    \"\"\"Calculates statutory tax.\"\"\"
    return amount * 0.2

print("Function Name:", calculate_tax.__name__)
print("Function Doc: ", calculate_tax.__doc__)
print("Function Annotations:", calculate_tax.__annotations__)
print("Underlying unwrapped function:", calculate_tax.__wrapped__)
"""),

    md_cell("""#### Observe
`calculate_tax.__name__` remains `'calculate_tax'` and `__wrapped__` provides a direct link to the original undecorated callable.

#### Recall Rule
> **Always decorate wrapper functions with `@functools.wraps` to preserve callable introspection and documentation.**
"""),

    # Experiment 1.8
    md_cell("""---
### Experiment 1.8 — Dynamic Stack Frame Interrogation (`sys._getframe`)
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
We inspect active CPython execution frames (`PyFrameObject`) to access caller namespaces without explicit parameter passing.

#### Mental Model
```text
Active Call Stack:
Frame 0: leaf_function()      [f_locals: {'msg': 'hello'}, f_back ──┐]
                                                                     │
Frame 1: caller_function()    [f_locals: {'secret_key': 'XYZ-123'}  ◄┘]
```

#### Code
We write a helper that queries its caller's local variables using `sys._getframe(1)`.
"""),

    code_cell("""import sys

def inspect_caller():
    # 0 = this function, 1 = caller function
    caller_frame = sys._getframe(1)
    print("Caller Function Name:", caller_frame.f_code.co_name)
    print("Caller Source Line:  ", caller_frame.f_lineno)
    print("Caller Local Variables:", caller_frame.f_locals)

def business_service():
    transaction_id = "TX-99812"
    user_id = 42
    inspect_caller()

business_service()
"""),

    md_cell("""#### Observe
`inspect_caller()` successfully read `transaction_id` and `user_id` directly from `business_service`'s active stack frame!

#### Explain
`sys._getframe()` provides a direct pointer into CPython's call stack. While powerful for debugging tools, profilers, and dynamic dependency injection, it relies on CPython-specific implementation internals.

#### Recall Rule
> **`sys._getframe(0)` accesses the active frame; `sys._getframe(1)` accesses the caller's frame via `f_back`.**
"""),

    md_cell("""---
## 3. Code-Reading & Prediction Section

Read each snippet, formulate your prediction mentally, and then execute the cell to verify.
"""),

    # Code Reading 1
    md_cell("""### Code-Reading 1.1 — Short-Circuit Reference Preservation
*Predict the exact returned value and type:*
```python
x = [] or "default"
y = [0] and {"key": "val"}
z = 0 or False or None or 42
```
"""),

    code_cell("""x = [] or "default"
y = [0] and {"key": "val"}
z = 0 or False or None or 42

print("x:", repr(x))
print("y:", repr(y))
print("z:", repr(z))
"""),

    md_cell("""**Mechanism**: Python's `and` and `or` operators do not return boolean `True`/`False` literals; they return the operand that terminated evaluation.
"""),

    # Code Reading 1.2
    md_cell("""### Code-Reading 1.2 — Walrus Operator in Expression Contexts
*Predict the output:*
"""),

    code_cell("""data = [1, 2, 3, 4, 5, 6, 7, 8]
filtered = [y for x in data if (y := x * 2) > 10]
print("Filtered:", filtered)
print("Leaked scope of y:", y)
"""),

    md_cell("""**Mechanism**: The assignment expression (`:=`) assigns and returns a value inside the comprehension filter, but leaks `y` into the enclosing scope (unlike standard comprehension target variables).
"""),

    md_cell("""---
## 4. Runtime Inspection Section

We systematically inspect bytecode instructions and opcode behaviors using `dis`.
"""),

    code_cell("""import dis

def loop_append(n):
    res = []
    for i in range(n):
        res.append(i)
    return res

def list_comp(n):
    return [i for i in range(n)]

print("=== Disassembly: Manual Loop Append ===")
dis.dis(loop_append)

print("\\n=== Disassembly: List Comprehension ===")
dis.dis(list_comp)
"""),

    md_cell("""### Disassembly Analysis
Notice why list comprehensions consistently outperform manual `for` loops appending to lists:
1. `loop_append` performs repeated attribute lookups (`LOAD_METHOD / CALL_METHOD` for `.append`) on every iteration.
2. `list_comp` uses specialized C-level bytecode instructions (`BUILD_LIST`, `LIST_APPEND`) directly manipulating the underlying C array without invoking method lookup mechanics.

---
### Chapter 1 Lab Complete!
You now have executable verification for CPython's execution model, reference binding, scoping rules, closures, and frame inspection.
""")
]

nb = make_notebook(cells)
validate_and_save(nb, "f:/notebook/libaray_fluency/01_Python_Execution_Core_Runtime_Lab.ipynb")
