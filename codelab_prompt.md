# MASTER PROMPT — BUILD 5 STANDALONE PYTHON LAB NOTEBOOKS

You now have access to:

1. The complete 5-chapter Python Revision & Mental-Model Book.
2. The restored Chapter 2.
3. The original source material used to create the book.

Your task is NOT to rewrite the reference book.

Your task is to create a separate executable laboratory companion consisting of exactly FIVE Jupyter notebooks:

* `01_Python_Execution_Core_Runtime_Lab.ipynb`
* `02_Python_Data_Model_Protocols_Lab.ipynb`
* `03_Library_Literacy_Inspection_Concurrency_Lab.ipynb`
* `04_Library_Composition_Architecture_Lab.ipynb`
* `05_Codebase_Dissection_Debugging_System_Composition_Lab.ipynb`

Each notebook corresponds directly to one chapter of the reference book.

## CORE PURPOSE

The reference book is my:

> COMPACT KNOWLEDGE / MENTAL-MODEL / REVISION LAYER

The notebooks are my:

> EXECUTABLE / EXPERIMENTAL / CODE-READING / OBSERVATION LAYER

Do NOT merge the notebooks into the book.

Do NOT make the book longer just to accommodate code.

Keep the book compact.

The notebooks should allow me to go from:

CONCEPT
→ READ CODE
→ PREDICT
→ RUN
→ OBSERVE
→ INSPECT
→ EXPLAIN
→ MODIFY
→ CONNECT

The ultimate goal is to become extremely strong at reading, understanding, inspecting, debugging, composing, and reasoning about Python code.

This is NOT a beginner Python course.

I already know Python fundamentals.

The labs should therefore emphasize Python mechanisms, runtime behavior, library literacy, advanced code reading, and system reasoning.

---

# IMPORTANT SOURCE RULE

Use the 5-chapter book as the primary organizational structure.

Use the original source PDFs/books as supporting material.

Do NOT randomly introduce unrelated Python topics simply because they exist in the source books.

Every experiment must connect to a concept in the reference book.

If a useful experiment requires information that is not adequately supported by the provided sources, clearly mark it as:

`[Supplementary implementation detail]`

Do not pretend it came from a source.

---

# NOTEBOOK DESIGN PRINCIPLE

Every notebook should function as a standalone LAB BOOK.

A user should be able to open:

`Chapter_X_Lab.ipynb`

without needing another notebook to understand what the experiment is demonstrating.

However, the lab should NOT reproduce the entire reference chapter.

For each topic:

1. SHORT CONCEPT REMINDER
2. MENTAL MODEL
3. CODE
4. PREDICT
5. RUN
6. OBSERVE OUTPUT
7. INSPECT
8. EXPLAIN
9. MODIFY / EXPERIMENT
10. CONNECTION TO THE REFERENCE BOOK

Use the book for compressed theory.

Use the notebook for execution and observation.

---

# REQUIRED NOTEBOOK STRUCTURE

Each notebook should contain:

## 0. Notebook Overview

Include:

* Chapter title
* Purpose of the laboratory
* What mechanisms will be investigated
* Prerequisites
* Python version assumptions
* Required libraries

Prefer Python standard library wherever possible.

Avoid unnecessary third-party dependencies.

---

## 1. Mental Model Map

Create a compact map of the chapter.

Example:

```text
source code
    ↓
parser
    ↓
AST
    ↓
code object
    ↓
frame
    ↓
bytecode execution
```

or:

```text
object
 ↓
attribute lookup
 ↓
descriptor?
 ↓
instance/class
 ↓
result
```

The map should orient me before I execute anything.

---

# EXPERIMENT FORMAT

For important mechanisms use this structure:

### Experiment X — [Name]

#### What are we investigating?

1–3 sentences.

#### Mental Model

Explain the mechanism briefly.

#### Code

Provide a small executable example.

#### Predict Before Running

Ask me to predict:

* output
* object identity
* mutation
* exception
* execution order
* lookup behavior
* frame state
* etc.

Do NOT turn this into a quiz section.

This is an experimental prompt immediately before execution.

#### Run

The executable code cell.

#### Observe

Show or explain the expected output.

#### Inspect

Use the appropriate Python inspection mechanism.

Examples:

```python
type()
id()
dir()
vars()
help()
inspect
dis
sys
sys.modules
sys._getframe()
```

or other appropriate standard-library tools.

#### Explain

Explain why the observed behavior occurred.

#### Modify

Where useful, provide one or two small modifications that allow me to change the behavior and observe the mechanism again.

#### Recall Rule

End with one compact rule.

Example:

> Assignment binds a name; it does not copy an object.

---

# CODE POLICY

Do NOT create code merely to increase the number of code cells.

Code must exist because execution materially improves understanding.

Prefer:

* 5–30 line focused experiments
* minimal reproducible examples
* standard-library code
* isolated mechanisms
* observable behavior

Avoid:

* giant applications
* boilerplate
* unnecessary classes
* unnecessary imports
* decorative code
* long tutorials
* copied textbook examples with irrelevant setup

When a mechanism requires a larger example, keep it as small as possible.

---

# CODE SOURCE POLICY

Use three categories:

### 1. SOURCE-DERIVED

An example directly based on a source example.

### 2. SOURCE-ADAPTED

A source concept/example simplified or rewritten for this laboratory.

### 3. ORIGINAL LAB EXPERIMENT

A new example created specifically to make the mechanism observable.

Clearly label the distinction when relevant.

Never fabricate attribution.

Do not copy large passages or large source-code examples merely because they exist in the books.

The objective is understanding, not reproduction.

---

# CHAPTER 1 LAB

Create experiments around:

* source → AST → code object → frame → bytecode
* names, bindings, references, objects
* identity/type/value
* mutability
* assignment
* copying
* `copy.copy`
* `copy.deepcopy`
* evaluation
* truthiness
* short-circuit evaluation
* functions
* LEGB
* closures
* closure cells
* decorators
* `functools.wraps`
* walrus operator
* runtime inspection

Important experiments should include:

* identity/reference behavior
* mutation vs rebinding
* shallow vs deep copy
* closure late binding
* `UnboundLocalError`
* closure cell inspection
* frame inspection
* `dis.dis()`
* AST inspection

Do not force every listed concept into a separate experiment.

Group related mechanisms when that produces a better learning sequence.

---

# CHAPTER 2 LAB

Create experiments around the Python Data Model and Protocols.

Include:

* iterable vs iterator
* `__iter__`
* `__next__`
* `StopIteration`
* generators
* `yield`
* `yield from`
* lazy evaluation
* generator state
* `gi_frame` where useful
* object construction
* `__new__`
* `__init__`
* inheritance
* MRO
* C3 linearization
* cooperative `super()`
* special methods
* operator protocols
* descriptors
* `__get__`
* `__set__`
* `__delete__`
* `__set_name__`
* properties
* attribute lookup
* `__getattribute__`
* `__getattr__`
* context managers
* `__enter__`
* `__exit__`
* exception suppression
* ABCs
* Protocol
* nominal vs structural typing

Especially include experiments that reveal:

```text
object
 ↓
protocol
 ↓
special method
 ↓
Python behavior
```

and:

```text
attribute access
 ↓
lookup
 ↓
descriptor?
 ↓
result
```

---

# CHAPTER 3 LAB

Focus on:

## Library Literacy

Create a reusable investigation workflow for an unfamiliar library/module.

Demonstrate tools such as:

```python
module.__file__
module.__all__
dir()
help()
vars()
inspect
inspect.signature()
inspect.getsource()
sys.modules
importlib
```

Also demonstrate what happens when source inspection is unavailable.

Cover:

* Python source modules
* packages
* compiled extensions
* documentation
* docstrings
* type stubs where appropriate
* dynamic imports
* module exports

Create one reusable:

> UNKNOWN LIBRARY INVESTIGATION SCRIPT

that I can copy and use when encountering an unfamiliar Python library.

## Standard Library

Use representative examples from important modules such as:

* pathlib
* collections
* itertools
* functools
* json
* sqlite3

Do NOT turn this into a catalog of every standard-library module.

Teach the pattern:

> How to recognize, inspect, understand and compose useful libraries.

## Concurrency

Create focused experiments for:

* GIL
* threading
* multiprocessing
* concurrent.futures
* CPU-bound vs I/O-bound work
* asyncio
* coroutine
* task
* event loop
* blocking vs non-blocking behavior

Show actual observable behavior rather than merely explaining terminology.

---

# CHAPTER 4 LAB

Focus on composition and architecture.

Include small pure-Python experiments demonstrating:

* composition
* interfaces
* adapters
* validation
* serialization
* dependency injection
* service layer
* repository
* unit of work
* persistence ignorance
* domain entities
* value objects
* domain events
* boundaries
* coupling/cohesion

Create ONE cohesive small architecture example where useful.

It should demonstrate how several concepts compose.

Avoid building a real web application.

Do NOT require:

Django
FastAPI
SQLAlchemy
Celery
or other external frameworks.

The point is to understand the architecture underneath frameworks.

---

# CHAPTER 5 LAB

This notebook is especially important.

It should train me to DISSECT unfamiliar Python systems.

Include experiments for:

* repository structure
* entry-point discovery
* import/dependency tracing
* call-chain tracing
* object/data/configuration flow
* source inspection
* `dis`
* frames
* debugging
* traceback interpretation
* profiling
* memory investigation
* framework/library "magic"
* decorators
* descriptors
* dynamic behavior
* multi-library composition

Create a reusable:

# PYTHON CODEBASE DISSECTION PROCEDURE

that I can apply to a real repository.

Include practical terminal/search patterns where appropriate, such as:

```text
find
rg
git grep
python -m ...
```

but do not make the notebook dependent on one specific operating system.

Create at least one miniature unfamiliar codebase inside the notebook or as a small generated example and demonstrate the complete investigation process:

```text
Repository
 ↓
Entry point
 ↓
Call chain
 ↓
Objects/data
 ↓
Domain logic
 ↓
Dependencies
 ↓
Adapters
 ↓
External boundary
```

The purpose is to practice the reasoning process.

---

# CODE-READING SECTION

Each notebook should contain a small number of high-value code-reading experiments.

Do NOT create dozens.

Choose particularly important examples involving:

* mutation
* closures
* generators
* MRO
* descriptors
* decorators
* context managers
* async
* library composition
* framework-like behavior

For each:

```text
READ
↓
PREDICT
↓
RUN
↓
COMPARE
↓
EXPLAIN
```

The goal is to make me better at reading unfamiliar Python code.

---

# INSPECTION SECTION

Where relevant, show actual outputs from tools.

Do not merely write:

"Use dis.dis()"

Actually execute:

```python
dis.dis(...)
```

and explain the important parts of the output.

Likewise for:

* `inspect`
* `sys`
* frames
* generators
* MRO
* descriptors
* profiling
* memory inspection

The notebook should make Python's behavior OBSERVABLE.

---

# OUTPUT REQUIREMENTS

Create exactly these five files:

```text
01_Python_Execution_Core_Runtime_Lab.ipynb
02_Python_Data_Model_Protocols_Lab.ipynb
03_Library_Literacy_Inspection_Concurrency_Lab.ipynb
04_Library_Composition_Architecture_Lab.ipynb
05_Codebase_Dissection_Debugging_System_Composition_Lab.ipynb
```

All must be valid `.ipynb` Jupyter Notebook files.

Every executable cell must contain valid Python.

Run/test the cells where practical before finalizing.

Do not leave placeholder code such as:

```python
# TODO
pass
...
```

unless the placeholder itself is intentionally being demonstrated.

---

# NOTEBOOK QUALITY CONTROL

Before finalizing each notebook, check:

1. Does every major experiment connect to the reference chapter?
2. Is the code actually executable?
3. Can I predict something before running it?
4. Can I observe something after running it?
5. Does the experiment reveal a mechanism rather than merely demonstrate syntax?
6. Is the example minimal?
7. Is unnecessary boilerplate removed?
8. Are outputs accurate?
9. Are source-derived/adapted examples correctly distinguished?
10. Does the notebook remain useful months later as a laboratory/reference?
11. Does it complement the book rather than duplicate it?
12. Does it train code-reading and reasoning rather than only code writing?

---

# MOST IMPORTANT CONSTRAINT

DO NOT TURN THESE NOTEBOOKS INTO FIVE TEXTBOOKS.

The reference book already contains the compressed theory.

The notebooks are the laboratory.

Therefore:

BOOK:

> "What is the mechanism?"

LAB:

> "Let's see the mechanism happen."

BOOK:

> "super() follows MRO."

LAB:

> "Let's construct the MRO, predict the call sequence, run it, inspect **mro**, and observe super()."

BOOK:

> "Generators suspend execution."

LAB:

> "Let's run a generator one step at a time and inspect its state."

BOOK:

> "Descriptors participate in attribute lookup."

LAB:

> "Let's build a tiny descriptor and trace what happens during attribute access."

BOOK:

> "Libraries can be dynamically inspected."

LAB:

> "Let's investigate an unfamiliar module using a repeatable procedure."

BOOK:

> "Dissect unfamiliar codebases systematically."

LAB:

> "Let's actually dissect one."

The final system should therefore be:

SOURCE BOOKS
↓
5-CHAPTER COMPACT REFERENCE BOOK
↓
5 STANDALONE EXECUTABLE LAB NOTEBOOKS
↓
PERSONAL PYTHON KNOWLEDGE SYSTEM

Optimize for:

UNDERSTANDING
+
RECALL
+
CODE READING
+
EXPERIMENTATION
+
INSPECTION
+
SYSTEM REASONING

—not page count and not code volume.
