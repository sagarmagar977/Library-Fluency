"""
Generates 05_Codebase_Dissection_Debugging_System_Composition_Lab.ipynb
"""
from build_notebook_helper import make_notebook, md_cell, code_cell, validate_and_save

cells = [
    md_cell("""# 05 — Codebase Dissection, Debugging & System Composition Laboratory

## 0. Notebook Overview

* **Chapter Correlation**: Chapter 5 — Codebase Dissection, Debugging & System Composition
* **Purpose**: Provide an executable training workbench to dissect unfamiliar Python repositories, trace runtime call-chains, profile CPU bottlenecks (`cProfile`), isolate memory leaks (`tracemalloc`), decompile bytecode (`dis`), manipulate zero-copy buffers (`memoryview`), unpack framework "magic", and execute a complete codebase dissection on a simulated miniature system.
* **Prerequisites**: Completion of Labs 01–04.
* **Python Version**: Python 3.10+ (tested on Python 3.14).
* **Required Libraries**: Standard library only (`dis`, `sys`, `tracemalloc`, `cProfile`, `pstats`, `inspect`, `pathlib`, `ast`).
* **Source Attribution Policy**:
  * `[SOURCE-DERIVED]`: Adapted from *Python Cookbook (3rd Ed)* (Debugging, Profiling, and Low-level Frames) and *Effective Python* (Memory Profiling and Performance).
  * `[SOURCE-ADAPTED]`: Codebase navigation heuristics synthesized from industry reverse-engineering patterns.
  * `[ORIGINAL LAB EXPERIMENT]`: Automated repository scanner and the simulated miniature codebase dissection walkthrough.
"""),

    md_cell("""## 1. Mental Model Map

```text
The 12-Step Codebase Dissection Sequence:
1. Manifests & Config   (pyproject.toml, setup.py, requirements.txt, .env)
       │
       ▼
2. Entry Points         (__main__.py, CLI commands, ASGI/WSGI app factories)
       │
       ▼
3. Call-Chain Tracing   (Controllers/Routers ──► Services ──► Domain Aggregates)
       │
       ▼
4. Data & Object Flow   (Ingress JSON ──► DTOs ──► Domain Entities ──► Repositories)
       │
       ▼
5. Dynamic Protocols    (Metaclasses, Descriptors, Decorator Stacks, Proxies)
       │
       ▼
6. Diagnostics & Audit  (Stack Frames, cProfile Bottlenecks, tracemalloc Leaks)
```
"""),

    md_cell("""---
## 2. Codebase Dissection & Diagnostics Experiments
"""),

    # Experiment 5.1
    md_cell("""### Experiment 5.1 — The Automated Codebase Dissection Scanner
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
We build a reusable Python script that scans any repository directory to locate entry points, identify top-level imports, and map architectural boundaries automatically.

#### Code
We implement the scanner and run it against our current workspace.
"""),

    code_cell("""from pathlib import Path
import ast

def scan_repository(repo_path="."):
    root = Path(repo_path)
    print(f"=== REPOSITORY SCAN: {root.resolve()} ===\\n")
    
    # 1. Manifest Discovery
    manifest_names = ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"]
    found_manifests = [p.name for p in root.iterdir() if p.name in manifest_names]
    print(f"Manifests Found: {found_manifests or 'None (Informal project layout)'}")
    
    # 2. Entry Point Discovery
    entry_points = []
    for py_file in root.rglob("*.py"):
        if py_file.name == "__main__.py":
            entry_points.append(str(py_file))
        else:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "if __name__ == '__main__':" in content or "if __name__ == \\"__main__\\":" in content:
                    entry_points.append(f"{py_file.name} (main block)")
            except Exception:
                pass
    print(f"Potential Entry Points: {entry_points}\\n")
    
    # 3. Top-Level Imports Discovery
    imports = set()
    for py_file in root.glob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        except Exception:
            pass
            
    print(f"Discovered Dependencies / Modules ({len(imports)}):")
    print(f"  {sorted(list(imports))}")

scan_repository(".")
"""),

    md_cell("""#### Recall Rule
> **Start codebase dissection at manifests and entry points before examining internal module implementations.**
"""),

    # Experiment 5.2
    md_cell("""---
### Experiment 5.2 — Tracing Call-Chains via Dynamic Stack Walking
*Category: [SOURCE-DERIVED - Python Cookbook Ch 14]*

#### What are we investigating?
When execution flow is obscured by decorators or dependency injection containers, we dynamically walk the execution call stack using `sys._getframe()` and `f_back`.

#### Code
We write a call-stack tracer and trigger it from nested functions.
"""),

    code_cell("""import sys

def print_call_chain():
    frame = sys._getframe(1)  # Caller frame
    print("=== DYNAMIC CALL-CHAIN TRACE ===")
    depth = 0
    while frame:
        code = frame.f_code
        print(f"  [{depth}] Function '{code.co_name}' in {code.co_filename}:{frame.f_lineno}")
        frame = frame.f_back
        depth += 1

def data_layer():
    print_call_chain()

def service_layer():
    data_layer()

def controller_layer():
    service_layer()

controller_layer()
"""),

    md_cell("""#### Observe
The function walked backward through `data_layer` $\rightarrow$ `service_layer` $\rightarrow$ `controller_layer` $\rightarrow$ module scope, exposing the complete dynamic call chain.

#### Recall Rule
> **`sys._getframe()` with `f_back` walking reveals active call chains when static inspection is obscured.**
"""),

    # Experiment 5.3
    md_cell("""---
### Experiment 5.3 — Bytecode Disassembly & Performance Insights
*Category: [SOURCE-DERIVED - Python Distilled Ch 4]*

#### What are we investigating?
We analyze why local variable lookup (`LOAD_FAST`) is substantially faster than global variable lookup (`LOAD_GLOBAL`) in CPython bytecode.

#### Code
We compare disassemblies of local vs global variable access in loops.
"""),

    code_cell("""import dis

GLOBAL_FACTOR = 1.05

def calc_with_global(items):
    return [x * GLOBAL_FACTOR for x in items]

def calc_with_cached_local(items):
    factor = GLOBAL_FACTOR  # Cache global in local slot!
    return [x * factor for x in items]

print("=== Bytecode: Global Access in Loop ===")
dis.dis(calc_with_global)

print("\\n=== Bytecode: Cached Local Access in Loop ===")
dis.dis(calc_with_cached_local)
"""),

    md_cell("""#### Observe
In `calc_with_cached_local`, the variable is loaded from a local slot via `LOAD_FAST` (fast array index lookup in C), whereas global lookup requires `LOAD_GLOBAL` (hash table lookup in `f_globals` then `f_builtins`).

#### Recall Rule
> **Local variables use fast array indexing (`LOAD_FAST`); global variables require dictionary lookups (`LOAD_GLOBAL`).**
"""),

    # Experiment 5.4
    md_cell("""---
### Experiment 5.4 — Profiling Bottlenecks with `cProfile`
*Category: [SOURCE-DERIVED - Python Cookbook Ch 14]*

#### What are we investigating?
We pinpoint exact CPU execution bottlenecks using deterministic profiling with `cProfile` and `pstats`.

#### Code
We profile an algorithmic bottleneck and analyze call counts and cumulative time (`cumtime`).
"""),

    code_cell("""import cProfile
import pstats
import time

def fast_worker():
    return sum(range(10_000))

def slow_bottleneck():
    time.sleep(0.05)  # Simulated I/O or algorithmic bottleneck
    return sum(range(100_000))

def orchestrator():
    for _ in range(3):
        fast_worker()
    slow_bottleneck()

# Profile orchestrator execution
profiler = cProfile.Profile()
profiler.enable()
orchestrator()
profiler.disable()

# Print sorted stats
stats = pstats.Stats(profiler).sort_stats("cumtime")
stats.print_stats(6)
"""),

    md_cell("""#### Observe
The profile clearly separates `tottime` (time spent in the function body itself) from `cumtime` (cumulative time including sub-functions), immediately pinpointing `slow_bottleneck`.

#### Recall Rule
> **Always profile before optimizing: sort `cProfile` stats by `cumtime` to identify true system bottlenecks.**
"""),

    # Experiment 5.5
    md_cell("""---
### Experiment 5.5 — Memory Leak Diagnostics with `tracemalloc`
*Category: [SOURCE-DERIVED - Effective Python Item 80]*

#### What are we investigating?
We take memory snapshots before and after a workload to isolate heap allocation spikes and memory leaks.

#### Code
We simulate a memory leak via a global container cache and compare snapshots.
"""),

    code_cell("""import tracemalloc

# Start tracking heap allocations
tracemalloc.start()

snapshot_before = tracemalloc.take_snapshot()

# Simulate a memory leak in a global cache
LEAK_CACHE = []
for i in range(10_000):
    LEAK_CACHE.append({"id": i, "payload": "x" * 64})

snapshot_after = tracemalloc.take_snapshot()

# Compare memory allocation delta
top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

print("=== TOP ALLOCATION DELTAS ===")
for stat in top_stats[:3]:
    print(stat)

tracemalloc.stop()
"""),

    md_cell("""#### Observe
`tracemalloc` highlighted the exact line number responsible for the memory increase (`LEAK_CACHE.append`).

#### Recall Rule
> **Use `tracemalloc.take_snapshot()` and `compare_to('lineno')` to detect memory leaks and allocation spikes.**
"""),

    # Experiment 5.6
    md_cell("""---
### Experiment 5.6 — Zero-Copy Buffer Protocol (`memoryview`)
*Category: [SOURCE-DERIVED - Fluent Python Ch 2]*

#### What are we investigating?
We demonstrate zero-copy binary slicing using `memoryview` and `bytearray`, eliminating memory copying overhead during large data processing.

#### Code
We slice a binary buffer and prove that no new memory is allocated.
"""),

    code_cell("""# Allocate binary data
data = bytearray(b"HEADER:PAYLOAD_BINARY_DATA_BLOCK:FOOTER")

# 1. Standard bytes slice copies data
standard_slice = data[7:28]
print(f"Standard slice: {standard_slice}")
standard_slice[0] = ord("X")  # Mutates copy, original untouched
print(f"Original after slice mutate: {data[:12]}")

# 2. memoryview creates a zero-copy view over the same RAM
view = memoryview(data)
sub_view = view[7:28]
print(f"\\nZero-copy sub_view: {sub_view.tobytes()}")

# Mutate through the view
sub_view[0] = ord("Z")
print(f"Original directly mutated via view: {data[:12]} (Zero-copy in-place!)")
"""),

    md_cell("""#### Recall Rule
> **`memoryview` creates a zero-copy view over existing buffer memory, allowing slicing and in-place mutation without copying.**
"""),

    # Experiment 5.7
    md_cell("""---
### Experiment 5.7 — Unpacking Framework Magic: Unwrapping Decorators & Proxies
*Category: [SOURCE-DERIVED - Python Cookbook Ch 9]*

#### What are we investigating?
We unpack framework decorators using `inspect.unwrap()`, and dissect dynamic proxies that delegate via `__getattr__`.

#### Code
"""),

    code_cell("""import functools
import inspect

def audit_decorator(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@audit_decorator
def core_business_calculation(a, b):
    \"\"\"Pure business logic.\"\"\"
    return a * b + 10

# 1. Unwrapping stacked decorators
raw_func = inspect.unwrap(core_business_calculation)
print("Wrapped Function:  ", core_business_calculation)
print("Raw Unwrapped Func:", raw_func)
print("Unwrapped is original:", raw_func is core_business_calculation.__wrapped__)

# 2. Dissecting a Framework Dynamic Proxy
class RequestProxy:
    def __init__(self, request_data):
        self._data = request_data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"No attribute {name}")

proxy = RequestProxy({"auth_user": "admin", "method": "POST"})
print("\\nProxy auth_user:", proxy.auth_user)
print("Proxy method:   ", proxy.method)
"""),

    md_cell("""#### Recall Rule
> **Use `inspect.unwrap()` to bypass decorator stacks and retrieve the raw underlying function.**
"""),

    # Experiment 5.8
    md_cell("""---
### Experiment 5.8 — Simulated Miniature Codebase Dissection Walkthrough
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
We construct a self-contained miniature microservice codebase directly in this notebook and execute the 12-Step Dissection Algorithm end-to-end.

#### Code
"""),

    code_cell("""# === THE MINIATURE CODEBASE ===

# [Module: domain.py]
class Account:
    def __init__(self, account_id: str, balance: float):
        self.account_id = account_id
        self.balance = balance

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

# [Module: repository.py]
class AccountRepository:
    def __init__(self):
        self._db = {"ACC-001": Account("ACC-001", 500.0)}

    def get(self, acc_id: str) -> Account:
        return self._db[acc_id]

# [Module: service.py]
def transfer_service(acc_id: str, amount: float, repo: AccountRepository):
    acc = repo.get(acc_id)
    acc.withdraw(amount)
    return acc.balance

# [Module: entrypoint_api.py]
def handle_http_request(payload: dict):
    # Entry Point Handler
    repo = AccountRepository()
    return transfer_service(payload["account_id"], payload["amount"], repo)

# === EXECUTING THE DISSECTION ===
print("1. Entry Point Invocation:")
response = handle_http_request({"account_id": "ACC-001", "amount": 150.0})
print(f" -> Transfer success! Remaining balance: {response}")
"""),

    md_cell("""#### Dissection Analysis
1. **Entry Point**: `handle_http_request` receives JSON dictionary ingress.
2. **Service Layer**: `transfer_service` coordinates validation and domain execution.
3. **Core Domain**: `Account.withdraw()` enforces business invariants (no overdraft).
4. **Persistence**: `AccountRepository` provides decoupled data access.

---
## 3. Code-Reading & Prediction Section
"""),

    # Code Reading 5.1
    md_cell("""### Code-Reading 5.1 — Disassembly Prediction
*Predict which operation emits `BUILD_LIST` and `LIST_APPEND` vs `CALL_METHOD`:*
"""),

    code_cell("""def f1():
    res = []
    for i in range(5):
        res.append(i)
    return res

def f2():
    return [i for i in range(5)]

print("Does f2 contain LIST_APPEND?")
opnames = [instr.opname for instr in dis.get_instructions(f2)]
print("LIST_APPEND in f2 opcodes:", "LIST_APPEND" in opnames)
"""),

    md_cell("""---
## 4. Runtime Inspection Section

We inspect active Python memory allocations and garbage collection statistics.
"""),

    code_cell("""import gc

print("GC Thresholds (Gen 0, Gen 1, Gen 2):", gc.get_threshold())
print("GC Object Count:                     ", gc.get_count())
"""),

    md_cell("""---
### Chapter 5 Lab Complete!
You now have working experimental tools for repository scanning, stack walking, bytecode disassembly, CPU profiling, memory leak tracking, and framework magic dissection.
""")
]

nb = make_notebook(cells)
validate_and_save(nb, "f:/notebook/libaray_fluency/05_Codebase_Dissection_Debugging_System_Composition_Lab.ipynb")
