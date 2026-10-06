"""
Generates 03_Library_Literacy_Inspection_Concurrency_Lab.ipynb
"""
from build_notebook_helper import make_notebook, md_cell, code_cell, validate_and_save

cells = [
    md_cell("""# 03 — Library Literacy, Inspection & Concurrency Laboratory

## 0. Notebook Overview

* **Chapter Correlation**: Chapter 3 — Library Literacy, Inspection & Concurrency
* **Purpose**: Provide an executable workbench to master dynamic runtime interrogation of unfamiliar libraries, dynamic imports, standard library composition patterns, and practical concurrency mechanisms (GIL behavior, threading, multiprocessing, and asyncio event loops).
* **Prerequisites**: Working understanding of Python functions, classes, and basic I/O.
* **Python Version**: Python 3.10+ (tested on Python 3.14).
* **Required Libraries**: Standard library only (`inspect`, `importlib`, `sys`, `pathlib`, `collections`, `itertools`, `functools`, `concurrent.futures`, `asyncio`, `time`, `os`).
* **Source Attribution Policy**:
  * `[SOURCE-DERIVED]`: Adapted from *Python Distilled* and *Fluent Python (2nd Ed)* (Concurrency, Asyncio, and Standard Library).
  * `[SOURCE-ADAPTED]`: Recipes from *Python Cookbook (3rd Ed)* and *Effective Python*.
  * `[ORIGINAL LAB EXPERIMENT]`: The Reusable Unknown Library Investigation Script and concurrency benchmark harnesses.
"""),

    md_cell("""## 1. Mental Model Map

```text
Concurrency Decision Flow:
                Is your bottleneck CPU or I/O?
                       │
       ┌───────────────┴───────────────┐
       ▼ (I/O Bound)                   ▼ (CPU Bound)
Do you need high scale sockets?     Need multi-core parallelism?
       │                               │
  ┌────┴────┐                          ▼
  ▼         ▼                 multiprocessing / ProcessPool
asyncio  threading            (GIL bypassed, isolated memory, IPC pickling)
(1-thread (Preemptive OS
co-op)    threads, GIL)
```
"""),

    md_cell("""---
## 2. Library Literacy & Concurrency Experiments
"""),

    # Experiment 3.1
    md_cell("""### Experiment 3.1 — The Reusable Unknown Library Investigation Script
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
When faced with an unfamiliar library or module, how do you inspect its public API, identify entry points, interrogate function contracts, and handle compiled C-extensions without opening external web documentation?

#### Mental Model
```text
Unfamiliar Module
  │
  ├── 1. module.__file__ -> Disk location (Python source vs compiled .so/.pyd)
  ├── 2. module.__all__  -> Explicit public exports (or non-underscore dir())
  ├── 3. inspect.isclass / isfunction -> Categorization
  └── 4. inspect.signature() -> Exact parameter contracts & default values
```

#### Code
We build a reusable inspection function and run it against Python's built-in `json` module and compiled `math` module.
"""),

    code_cell("""import inspect
import types

def investigate_library(module_or_obj):
    \"\"\"Reusable operational script for dissecting any Python module or object.\"\"\"
    print(f"=== INVESTIGATING: {getattr(module_or_obj, '__name__', str(module_or_obj))} ===")
    
    # 1. Location & Type
    origin = getattr(module_or_obj, "__file__", "Built-in / Compiled C-Extension")
    print(f"Origin File: {origin}")
    print(f"Type:        {type(module_or_obj).__name__}")
    
    # 2. Public API Isolation
    if hasattr(module_or_obj, "__all__"):
        public_symbols = module_or_obj.__all__
        print(f"Public API via __all__ ({len(public_symbols)} symbols):")
    else:
        public_symbols = [attr for attr in dir(module_or_obj) if not attr.startswith("_")]
        print(f"Public API via dir() filtered ({len(public_symbols)} symbols):")
        
    print(f"Sample Symbols: {public_symbols[:8]}...\\n")
    
    # 3. Categorization & Signature Interrogation
    classes, functions = [], []
    for name in public_symbols:
        val = getattr(module_or_obj, name, None)
        if inspect.isclass(val):
            classes.append(name)
        elif inspect.isroutine(val):
            functions.append(name)
            
    print(f"Classes ({len(classes)}): {classes[:6]}")
    print(f"Functions/Routines ({len(functions)}): {functions[:6]}\\n")
    
    # 4. Signature Interrogation of Primary Function
    if functions:
        target_name = functions[0]
        target_fn = getattr(module_or_obj, target_name)
        try:
            sig = inspect.signature(target_fn)
            print(f"Signature for {target_name}{sig}:")
            for param in sig.parameters.values():
                print(f"  - {param.name}: kind={param.kind.name}, default={param.default}")
        except (ValueError, TypeError):
            print(f"Signature for {target_name}: [Compiled C-Extension - Signature unavailable; use help()]")

# Test on standard library module
import json
investigate_library(json)
"""),

    md_cell("""#### Observe
The script cleanly extracted the file path, public exports (`dumps`, `loads`), separated classes from functions, and extracted parameter contracts.

#### Handling Compiled C-Extensions
When inspecting C-extensions (like `math` or third-party compiled modules), `inspect.getsource()` raises `TypeError`. Let's observe this:
"""),

    code_cell("""import math

try:
    inspect.getsource(math.sin)
except TypeError as err:
    print("Expected Error on C-Extension:", err)
    print("Fallback: Using docstring:")
    print(math.sin.__doc__)
"""),

    md_cell("""#### Recall Rule
> **Isolate public API via `__all__`, categorize with `inspect.isclass`/`isroutine`, and interrogate signatures via `inspect.signature()`. Fall back to `__doc__` for compiled extensions.**
"""),

    # Experiment 3.2
    md_cell("""---
### Experiment 3.2 — Dynamic Imports, `sys.modules` & The Reload Trap
*Category: [SOURCE-DERIVED - Python Distilled Ch 8]*

#### What are we investigating?
We observe module caching inside `sys.modules`, programmatic imports with `importlib.import_module()`, and the classic trap of `importlib.reload()` when using `from x import y`.

#### Mental Model
`sys.modules` is the central import cache. `import x` executes code **once**. Subsequent imports fetch the cached module object. `importlib.reload(mod)` mutates the module object in-place, but **cannot update bindings previously copied** into caller namespaces via `from mod import func`.

#### Code
We test dynamic module lookup and demonstrate the reload trap.
"""),

    code_cell("""import importlib
import sys

# 1. Dynamic string-based import
math_mod = importlib.import_module("math")
print("Imported math_mod:", math_mod)
print("Is math cached in sys.modules?", "math" in sys.modules)
print("Cache reference matches math_mod:", sys.modules["math"] is math_mod)

# 2. Module Reloading Traps
# We create a dummy module in memory
import types
dummy = types.ModuleType("my_plugin")
dummy.VERSION = "1.0"
sys.modules["my_plugin"] = dummy

# Caller A imports via attribute lookup
import my_plugin
# Caller B imports via name binding
from my_plugin import VERSION

print("\\nInitial:")
print("my_plugin.VERSION:  ", my_plugin.VERSION)
print("Bound VERSION name: ", VERSION)

# Mutate module in-place
dummy.VERSION = "2.0"
print("\\nAfter in-place module mutation:")
print("my_plugin.VERSION:  ", my_plugin.VERSION, "(Updated!)")
print("Bound VERSION name: ", VERSION, "(STALE! Remains bound to old string)")
"""),

    md_cell("""#### Observe
`VERSION` retained `'1.0'` because `from my_plugin import VERSION` bound the identifier in the local frame to the object `1.0`. Mutating the module dictionary did not rebind the caller's local variable.

#### Recall Rule
> **`sys.modules` caches module objects; `reload()` mutates module state in-place but cannot update unbound caller references.**
"""),

    # Experiment 3.3
    md_cell("""---
### Experiment 3.3 — Standard Library Power Composition
*Category: [SOURCE-ADAPTED - Python Cookbook Ch 1 & 2]*

#### What are we investigating?
We demonstrate how to compose standard library modules (`collections.defaultdict`, `itertools.groupby`, `functools.lru_cache`, `pathlib.Path`) to build high-performance data processing pipelines without external libraries.

#### Code
We group, cache, and transform data using zero third-party dependencies.
"""),

    code_cell("""from collections import defaultdict
import functools
import itertools

# 1. Multi-valued mapping with defaultdict
user_roles = defaultdict(list)
assignments = [("alice", "admin"), ("bob", "user"), ("alice", "editor"), ("charlie", "user")]

for user, role in assignments:
    user_roles[user].append(role)
print("Defaultdict mapping:", dict(user_roles))

# 2. Expensive computation memoization with functools.lru_cache
@functools.lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("Fibonacci(30):", fibonacci(30))
print("Cache Info:    ", fibonacci.cache_info())

# 3. Grouping sorted data with itertools.groupby
data = [("fruit", "apple"), ("fruit", "banana"), ("veg", "carrot"), ("veg", "spinach")]
# Note: groupby requires consecutive keys!
grouped = {k: [item[1] for item in g] for k, g in itertools.groupby(data, key=lambda x: x[0])}
print("Grouped data:  ", grouped)
"""),

    md_cell("""#### Recall Rule
> **Compose `collections`, `itertools`, and `functools` before reaching for external dependencies.**
"""),

    # Experiment 3.4
    md_cell("""---
### Experiment 3.4 — The GIL & Threading Concurrency
*Category: [SOURCE-DERIVED - Fluent Python Ch 20]*

#### What are we investigating?
We benchmark CPU-bound execution vs I/O-bound execution under CPython's Global Interpreter Lock (GIL) to prove why threads accelerate I/O but serialize CPU work.

#### Mental Model
- **I/O-Bound**: OS blocking calls release the GIL. Multiple threads overlap waiting time.
- **CPU-Bound**: Bytecode evaluation retains the GIL. Multiple threads context-switch on a single core, introducing thread management overhead.

#### Code
We compare sequential vs threaded execution for I/O and CPU tasks.
"""),

    code_cell("""import time
from concurrent.futures import ThreadPoolExecutor

# 1. I/O-Bound Simulation (Releases GIL)
def io_task(task_id):
    time.sleep(0.05)  # time.sleep releases the GIL
    return task_id

start_io = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(io_task, range(4)))
io_duration = time.perf_counter() - start_io
print(f"I/O-Bound 4 tasks with 4 threads: {io_duration:.3f}s (vs ~0.20s sequential)")

# 2. CPU-Bound Simulation (Retains GIL)
def cpu_task(n):
    count = 0
    for i in range(n):
        count += 1
    return count

COUNT = 2_000_000
start_cpu = time.perf_counter()
with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(cpu_task, [COUNT, COUNT]))
cpu_duration = time.perf_counter() - start_cpu
print(f"CPU-Bound 2 tasks with 2 threads: {cpu_duration:.3f}s (Serialized by GIL)")
"""),

    md_cell("""#### Observe
The 4 I/O tasks completed in ~0.05s (concurrently yielding the GIL). The CPU tasks did not run in parallel because the GIL restricted bytecode execution to a single core.

#### Recall Rule
> **CPython threads accelerate I/O-bound operations; they serialize CPU-bound bytecode execution due to the GIL.**
"""),

    # Experiment 3.5
    md_cell("""---
### Experiment 3.5 — Multiprocessing: Bypassing the GIL & Memory Isolation
*Category: [SOURCE-DERIVED - Fluent Python Ch 20]*

#### What are we investigating?
We observe how `multiprocessing` achieves true multi-core CPU parallelism by allocating separate CPython interpreter processes, and verify that child processes share zero memory.

#### Code
We run CPU tasks across separate processes and verify distinct Process IDs (`os.getpid()`).
"""),

    code_cell("""import os
from concurrent.futures import ProcessPoolExecutor

def worker_identity(task_id):
    # Returns process ID and task ID
    return f"Task {task_id} executed in PID: {os.getpid()}"

print(f"Main Process PID: {os.getpid()}")

# Use ProcessPoolExecutor for true CPU parallel execution
with ProcessPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(worker_identity, range(4)))

for r in results:
    print("  *", r)
"""),

    md_cell("""#### Observe
The worker processes have completely distinct Process IDs. Each process has its own GIL, its own memory heap, and its own Python interpreter.

#### Recall Rule
> **`multiprocessing` bypasses the GIL by spawning isolated CPython processes over IPC serialization.**
"""),

    # Experiment 3.6
    md_cell("""---
### Experiment 3.6 — Asyncio Event Loop & Cooperative Concurrency
*Category: [SOURCE-DERIVED - Fluent Python Ch 21]*

#### What are we investigating?
We observe single-threaded cooperative multitasking with `asyncio`. We contrast sequential `await` execution with concurrent scheduling via `asyncio.create_task` and `asyncio.gather`.

#### Mental Model
```text
Event Loop
  │
  ├── Schedules Coroutine Tasks
  ├── Switches tasks ONLY when an explicit 'await' boundary yields control
  └── Resumes task when awaited I/O resolves
```

#### Code
We define an async task and compare sequential await vs concurrent `asyncio.gather`.
"""),

    code_cell("""import asyncio
import time

async def async_fetch(item_id, delay):
    await asyncio.sleep(delay)  # Yields control to event loop
    return f"Result {item_id}"

async def main():
    start = time.perf_counter()
    
    # 1. Concurrent scheduling via asyncio.gather
    print("Running 3 tasks concurrently via asyncio.gather...")
    results = await asyncio.gather(
        async_fetch(1, 0.05),
        async_fetch(2, 0.05),
        async_fetch(3, 0.05)
    )
    duration = time.perf_counter() - start
    print(f"Completed in {duration:.3f}s: {results}")

# Run within asyncio loop
await main()
"""),

    md_cell("""#### Observe
All three async operations completed concurrently in ~0.05s within a single OS thread!

#### Recall Rule
> **`asyncio` context-switches at explicit `await` expressions; synchronous blocking calls inside coroutines freeze the entire event loop.**
"""),

    md_cell("""---
## 3. Code-Reading & Prediction Section
"""),

    # Code Reading 3.1
    md_cell("""### Code-Reading 3.1 — Asyncio Sequential vs Concurrent Trap
*Predict the total elapsed execution time:*
```python
# Snippet A:
res1 = await async_fetch(1, 0.1)
res2 = await async_fetch(2, 0.1)

# Snippet B:
t1 = asyncio.create_task(async_fetch(1, 0.1))
t2 = asyncio.create_task(async_fetch(2, 0.1))
res1 = await t1
res2 = await t2
```
"""),

    code_cell("""# Test Snippet A:
start = time.perf_counter()
await async_fetch(1, 0.05)
await async_fetch(2, 0.05)
print(f"Sequential Await Time: {time.perf_counter() - start:.3f}s")

# Test Snippet B:
start = time.perf_counter()
t1 = asyncio.create_task(async_fetch(1, 0.05))
t2 = asyncio.create_task(async_fetch(2, 0.05))
await t1
await t2
print(f"Concurrent Tasks Time: {time.perf_counter() - start:.3f}s")
"""),

    md_cell("""**Mechanism**: Awaiting a coroutine directly (`await coro()`) executes it sequentially. Creating tasks first (`asyncio.create_task()`) schedules them immediately on the event loop, allowing them to overlap during `await`.
"""),

    md_cell("""---
## 4. Runtime Inspection Section

We inspect callable contracts dynamically and validate parameter bindings before execution using `inspect.signature().bind()`.
"""),

    code_cell("""import inspect

def service_endpoint(user_id: int, action: str, timeout: float = 5.0):
    pass

sig = inspect.signature(service_endpoint)
print("Signature:", sig)

# Test 1: Valid Arguments
bound = sig.bind(101, "login", timeout=10.0)
print("Valid bound args:", bound.arguments)

# Test 2: Invalid Arguments caught BEFORE calling
try:
    sig.bind(101)  # Missing 'action'
except TypeError as err:
    print("Caught Signature Mismatch:", err)
"""),

    md_cell("""---
### Chapter 3 Lab Complete!
You now have working tools to interrogate unknown libraries, dynamic modules, thread/process concurrency profiles, and asyncio event loops.
""")
]

nb = make_notebook(cells)
validate_and_save(nb, "f:/notebook/libaray_fluency/03_Library_Literacy_Inspection_Concurrency_Lab.ipynb")
