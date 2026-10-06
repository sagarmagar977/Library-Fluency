"""
Generates 02_Python_Data_Model_Protocols_Lab.ipynb
"""
from build_notebook_helper import make_notebook, md_cell, code_cell, validate_and_save

cells = [
    md_cell("""# 02 — Python Data Model & Object Protocols Laboratory

## 0. Notebook Overview

* **Chapter Correlation**: Chapter 2 — The Python Data Model & Object Protocols
* **Purpose**: Provide an executable, observable experimental laboratory to inspect Python's protocol-driven object model: iteration mechanics, generator frame suspension, `__new__` allocation vs `__init__` initialization, MRO C3 linearization, data vs non-data descriptors, attribute lookup interception, context management, and structural typing.
* **Prerequisites**: Completion of Chapter 1 Lab; familiarity with Python class syntax.
* **Python Version**: Python 3.10+ (tested on Python 3.14).
* **Required Libraries**: Standard library only (`inspect`, `contextlib`, `abc`, `typing`).
* **Source Attribution Policy**:
  * `[SOURCE-DERIVED]`: Adapted from *Fluent Python (2nd Ed)* (Chapters on Data Model, Special Methods, Iteration, and Descriptors).
  * `[SOURCE-ADAPTED]`: Simplified examples from *Python Cookbook (3rd Ed)* and *Python Distilled*.
  * `[ORIGINAL LAB EXPERIMENT]`: Targeted protocol tracing and lookup sequence scripts.
"""),

    md_cell("""## 1. Mental Model Map

```text
Special Method Invocation Sequence:
User Operation (e.g. for x in obj / obj.attr / with cm)
       │
       ▼
CPython Protocol Dispatcher
       │
       ▼
Class Dictionary / MRO Check for Dunder Method (__iter__, __get__, __enter__)
       │
       ├── Found -> Execute method with underlying CPython invariants
       └── Missing -> Fallback mechanism (e.g. __getitem__, __getattr__) or TypeError
```
"""),

    md_cell("""---
## 2. Core Protocol Experiments
"""),

    # Experiment 2.1
    md_cell("""### Experiment 2.1 — The Iteration Protocol & `__getitem__` Fallback
*Category: [SOURCE-DERIVED - Fluent Python Ch 1 & 17]*

#### What are we investigating?
We observe the precise protocol Python executes during iteration (`iter(x)`), distinguishing between an **Iterable** (defines `__iter__`) and an **Iterator** (defines `__next__` and `__iter__`), and testing the legacy `__getitem__` fallback.

#### Mental Model
```text
iter(obj)
  │
  ├── 1. obj.__iter__() exists? -> Returns Iterator (implements __next__)
  │
  └── 2. obj.__getitem__(i) exists? -> Falls back to calling obj[0], obj[1]... until IndexError
```

#### Code
We build a custom iterator class, inspect its step-by-step state, and then test an object that only implements `__getitem__`.
"""),

    code_cell("""# 1. Custom Iterable & Iterator
class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        # Must return an iterator object
        return CountdownIterator(self.start)

class CountdownIterator:
    def __init__(self, count):
        self.count = count

    def __iter__(self):
        return self

    def __next__(self):
        if self.count <= 0:
            raise StopIteration
        val = self.count
        self.count -= 1
        return val

# Step-by-step iteration
cd = Countdown(3)
it = iter(cd)
print("Type of cd:", type(cd))
print("Type of it:", type(it))
print("next(it):", next(it))
print("next(it):", next(it))
print("next(it):", next(it))

try:
    next(it)
except StopIteration:
    print("Caught StopIteration cleanly!")
"""),

    md_cell("""Now observe the `__getitem__` fallback mechanism:
"""),

    code_cell("""# 2. Legacy fallback iterable via __getitem__
class IndexableSequence:
    def __init__(self, items):
        self._items = items

    def __getitem__(self, index):
        # Python calls index 0, 1, 2... until IndexError
        return self._items[index]

seq = IndexableSequence(["alpha", "beta", "gamma"])
print("Is __iter__ in class?", "__iter__" in dir(seq))
print("Iteration via for loop:")
for item in seq:
    print(" ->", item)
"""),

    md_cell("""#### Observe
Even though `IndexableSequence` defines no `__iter__`, `iter(seq)` automatically synthesizes an iterator calling `seq[0]`, `seq[1]`, etc. until `IndexError` occurs!

#### Recall Rule
> **Iterables return iterators via `__iter__()` (falling back to `__getitem__`); Iterators yield values via `__next__()` and terminate with `StopIteration`.**
"""),

    # Experiment 2.2
    md_cell("""---
### Experiment 2.2 — Generators, Frame Suspension & `yield from`
*Category: [SOURCE-DERIVED - Fluent Python Ch 17]*

#### What are we investigating?
We inspect how generator functions suspend execution frames across `yield` statements, query generator state via `inspect`, and trace sub-generator delegation with `yield from`.

#### Mental Model
A function with `yield` returns a generator object. When executed, it pauses at `yield`, preserving its stack frame (`gi_frame`), local variables, and instruction pointer.

#### Code
We step through a generator and inspect its frame state. Then we test `yield from` capturing a returned value.
"""),

    code_cell("""import inspect

def generator_state_demo():
    x = 10
    yield x
    x = 20
    yield x
    return "FINISHED"

gen = generator_state_demo()
print("Initial state:", inspect.getgeneratorstate(gen))

# Step 1
val1 = next(gen)
print(f"Yielded: {val1}, State: {inspect.getgeneratorstate(gen)}")
print("Frame locals inside generator:", gen.gi_frame.f_locals)

# Step 2
val2 = next(gen)
print(f"Yielded: {val2}, State: {inspect.getgeneratorstate(gen)}")
print("Frame locals inside generator:", gen.gi_frame.f_locals)

# Step 3: Termination
try:
    next(gen)
except StopIteration as e:
    print("State:", inspect.getgeneratorstate(gen))
    print("StopIteration return value:", e.value)
"""),

    md_cell("""Now observe two-way delegation with `yield from`:
"""),

    code_cell("""def sub_generator():
    yield "Sub A"
    yield "Sub B"
    return 999  # Return value captured by 'yield from'

def main_generator():
    yield "Main Start"
    result = yield from sub_generator()
    yield f"Main End (Sub returned {result})"

print("Full yield from stream:")
for item in main_generator():
    print("  *", item)
"""),

    md_cell("""#### Recall Rule
> **`yield` suspends the active execution frame; `yield from` delegates iteration and captures the sub-generator's return value.**
"""),

    # Experiment 2.3
    md_cell("""---
### Experiment 2.3 — Object Lifecycle: `__new__` vs `__init__`
*Category: [SOURCE-ADAPTED - Python Cookbook Ch 8]*

#### What are we investigating?
We observe instance allocation (`__new__`) preceding instance initialization (`__init__`), and implement a thread-safe Singleton and an immutable subclass.

#### Mental Model
```text
Class(*args, **kwargs)
       │
       ▼
instance = Class.__new__(Class, *args, **kwargs)  [Allocation]
       │
       ▼
if isinstance(instance, Class):
    Class.__init__(instance, *args, **kwargs)     [Initialization]
return instance
```

#### Code
We prove that `__init__` is skipped if `__new__` returns an object of another type, and construct a Singleton.
"""),

    code_cell("""class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("Allocating new instance in __new__...")
            cls._instance = super().__new__(cls)
        else:
            print("Returning existing cached instance...")
        return cls._instance

    def __init__(self, name):
        # NOTE: __init__ runs EVERY time Singleton() is called!
        self.name = name

s1 = Singleton("Instance-1")
print("s1 name:", s1.name)

s2 = Singleton("Instance-2")
print("s2 name:", s2.name)
print("s1 is s2:", s1 is s2)
print("s1 name now overwritten by s2 __init__:", s1.name)
"""),

    md_cell("""#### Observe
`s1 is s2` is `True`. But notice the trap: `__init__` was called on both invocations because `__new__` returned an instance of `Singleton`.

#### Customizing Immutable Types (`tuple`)
Immutable types cannot have their attributes populated in `__init__` because they are already created. We must use `__new__`:
"""),

    code_cell("""class UppercaseTuple(tuple):
    def __new__(cls, iterable):
        # Pre-process elements before tuple allocation
        upper_items = (str(x).upper() for x in iterable)
        return super().__new__(cls, upper_items)

ut = UppercaseTuple(["python", "protocols", "mental_models"])
print("UppercaseTuple:", ut)
"""),

    md_cell("""#### Recall Rule
> **`__new__` allocates and returns the object instance; `__init__` populates instance attributes and returns `None`.**
"""),

    # Experiment 2.4
    md_cell("""---
### Experiment 2.4 — Inheritance, MRO & Cooperative `super()`
*Category: [SOURCE-DERIVED - Python Distilled Ch 7 & Python Cookbook Ch 8]*

#### What are we investigating?
We analyze diamond inheritance and C3 linearization to observe why `super()` does not call the syntactic parent class, but delegates to the next class in the runtime caller's MRO.

#### Mental Model
```text
       Base
      /    \
     A      B
      \    /
        C
C.__mro__ = (C, A, B, Base, object)
Inside A: super().run() delegates to B, NOT Base!
```

#### Code
We build a diamond hierarchy with cooperative `super()` logging.
"""),

    code_cell("""class Base:
    def run(self):
        print(" -> Base.run()")

class A(Base):
    def run(self):
        print(" -> Enter A.run()")
        super().run()
        print(" -> Exit A.run()")

class B(Base):
    def run(self):
        print(" -> Enter B.run()")
        super().run()
        print(" -> Exit B.run()")

class C(A, B):
    def run(self):
        print(" -> Enter C.run()")
        super().run()
        print(" -> Exit C.run()")

print("MRO of class C:")
for idx, cls in enumerate(C.__mro__):
    print(f"  {idx}: {cls.__name__}")

print("\\nExecuting C().run():")
c = C()
c.run()
"""),

    md_cell("""#### Observe
Trace the execution:
`C` $\rightarrow$ `A` $\rightarrow$ `B` $\rightarrow$ `Base`!
Inside `A`, `super().run()` routed directly into `B`, which is a sibling class in the syntax tree, but the *next class* in `C`'s runtime MRO!

#### Recall Rule
> **`super()` delegates to the next class in the caller instance's runtime MRO sequence, not the syntactic parent.**
"""),

    # Experiment 2.5
    md_cell("""---
### Experiment 2.5 — The Descriptor Protocol: Data vs Non-Data Descriptors
*Category: [SOURCE-DERIVED - Fluent Python Ch 22 & 23]*

#### What are we investigating?
We demonstrate the fundamental rule of attribute lookup: **Data Descriptors (`__set__`) take precedence over the instance dictionary (`__dict__`), whereas Non-Data Descriptors (`__get__` only) yield precedence to `__dict__`.**

#### Mental Model
```text
Lookup: obj.attr
  1. Data Descriptor found on type(obj) MRO? -> Call Descriptor.__get__()
  2. 'attr' in obj.__dict__?                 -> Return obj.__dict__['attr']
  3. Non-Data Descriptor on type(obj) MRO?   -> Call Descriptor.__get__()
```

#### Code
We build a Data Descriptor and a Non-Data Descriptor on the same owner class and manipulate the instance `__dict__`.
"""),

    code_cell("""class DataDescriptor:
    def __init__(self, name):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return f"DataDescriptor({instance.__dict__.get(self.name)})"

    def __set__(self, instance, value):
        print(f"DataDescriptor.__set__ intercepted: {self.name} = {value}")
        instance.__dict__[self.name] = value

class NonDataDescriptor:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        return f"NonDataDescriptor({self.value})"

class Host:
    data_attr = DataDescriptor("data_attr")
    nondata_attr = NonDataDescriptor("default_val")

h = Host()
h.data_attr = 100
print("h.data_attr:", h.data_attr)
print("h.nondata_attr:", h.nondata_attr)

# Now inject values directly into instance __dict__
print("\\n--- Injecting directly into h.__dict__ ---")
h.__dict__["data_attr"] = "HACKED_DATA"
h.__dict__["nondata_attr"] = "SHADOWED_NONDATA"

print("After injection, h.data_attr:   ", h.data_attr)
print("After injection, h.nondata_attr:", h.nondata_attr)
"""),

    md_cell("""#### Observe
- `h.data_attr` still invoked `DataDescriptor.__get__()` despite the key existing in `h.__dict__`!
- `h.nondata_attr` was **shadowed** by `h.__dict__["nondata_attr"]` and returned `'SHADOWED_NONDATA'`!

#### Explain
Functions and methods in Python are non-data descriptors (they define `__get__` to bind to instances). This is why you can dynamically override an instance method by assigning a function to `instance.__dict__`!

#### Recall Rule
> **Data Descriptors (`__set__`) take precedence over instance `__dict__`; Non-Data Descriptors (`__get__` only) yield to instance `__dict__`.**
"""),

    # Experiment 2.6
    md_cell("""---
### Experiment 2.6 — Attribute Interception: `__getattribute__` vs `__getattr__`
*Category: [SOURCE-ADAPTED - Python Distilled Ch 7]*

#### What are we investigating?
We observe the difference between unconditional attribute interception (`__getattribute__`) and fallback failure handling (`__getattr__`).

#### Mental Model
- `__getattribute__(self, name)`: Intercepts **every single** attribute access attempt.
- `__getattr__(self, name)`: Invoked **only** when standard lookup fails (`AttributeError`).

#### Code
We build a proxy class and inspect invocation orders.
"""),

    code_cell("""class DynamicProxy:
    def __init__(self, target):
        super().__setattr__("_target", target)

    def __getattribute__(self, name):
        print(f"__getattribute__ invoked for: '{name}'")
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print(f"__getattr__ fallback invoked for: '{name}'")
        target = super().__getattribute__("_target")
        return getattr(target, name)

proxy = DynamicProxy({"alpha": 1, "beta": 2})

# 1. Access existing internal attribute
print("Accessing _target:")
_ = proxy._target

# 2. Access missing attribute forwarded to target dict
print("\\nAccessing 'keys' (forwarded to dict):")
keys_fn = proxy.keys
print("Keys result:", list(keys_fn()))
"""),

    md_cell("""#### Recall Rule
> **`__getattribute__` runs on every attribute access; `__getattr__` runs only when normal attribute lookup fails.**
"""),

    # Experiment 2.7
    md_cell("""---
### Experiment 2.7 — Context Managers & Exception Suppression
*Category: [SOURCE-DERIVED - Fluent Python Ch 18]*

#### What are we investigating?
We demonstrate `__enter__` and `__exit__`, and verify the rule of exception suppression: returning `True` from `__exit__` suppresses the exception.

#### Mental Model
```text
with CM() as target:
    body
  │
  ├── Normal Exit: CM.__exit__(None, None, None)
  │
  └── Exception Raised: CM.__exit__(exc_type, exc_val, exc_tb)
        ├── Returns True  -> Exception SUPPRESSED; execution continues cleanly
        └── Returns False -> Exception RE-RAISED
```

#### Code
We build a context manager that selectively silences specific errors.
"""),

    code_cell("""class SuppressErrors:
    def __init__(self, *suppressed_types):
        self.suppressed_types = suppressed_types

    def __enter__(self):
        print("[Enter context]")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[Exit context] Caught: {exc_type}")
        if exc_type is not None and issubclass(exc_type, self.suppressed_types):
            print(f" -> Suppressing {exc_type.__name__}!")
            return True  # Truthy return silences the exception!
        return False

print("Test 1: Suppressed ZeroDivisionError:")
with SuppressErrors(ZeroDivisionError):
    print("  Inside block: dividing by zero...")
    _ = 1 / 0
print("Execution resumed normally after suppressed error!\\n")

print("Test 2: Unsuppressed ValueError:")
try:
    with SuppressErrors(ZeroDivisionError):
        print("  Inside block: raising ValueError...")
        raise ValueError("Critical failure")
except ValueError:
    print("Caught unsuppressed ValueError outside with block!")
"""),

    md_cell("""#### Recall Rule
> **`__exit__` returning `True` suppresses caught exceptions; returning `False` or `None` re-raises them.**
"""),

    # Experiment 2.8
    md_cell("""---
### Experiment 2.8 — Nominal Subtyping (ABCs) vs Structural Subtyping (`typing.Protocol`)
*Category: [SOURCE-DERIVED - Fluent Python Ch 13]*

#### What are we investigating?
We compare Abstract Base Classes (nominal subtyping enforcing inheritance) with `typing.Protocol` (structural subtyping / static duck typing).

#### Mental Model
- **ABCs (Nominal)**: Class must explicitly inherit or register. Verified at instantiation time.
- **Protocols (Structural)**: Class does **not** inherit. Verified by shape/attributes at static analysis time, or at runtime with `@runtime_checkable`.

#### Code
We build both and test `isinstance()` checks.
"""),

    code_cell("""import abc
from typing import Protocol, runtime_checkable

# 1. Nominal: ABC
class AbstractSpeaker(abc.ABC):
    @abc.abstractmethod
    def speak(self) -> str:
        pass

# 2. Structural: Protocol
@runtime_checkable
class SpeakerProtocol(Protocol):
    def speak(self) -> str:
        ...

# Pure implementation without inheritance
class Dog:
    def speak(self) -> str:
        return "Woof!"

dog = Dog()
print("Dog inherits from AbstractSpeaker?", isinstance(dog, AbstractSpeaker))
print("Dog matches SpeakerProtocol?", isinstance(dog, SpeakerProtocol))
"""),

    md_cell("""#### Observe
`isinstance(dog, AbstractSpeaker)` is `False` because `Dog` did not explicitly inherit from the ABC. But `isinstance(dog, SpeakerProtocol)` is `True` because `Dog` satisfies the structural method contract!

#### Recall Rule
> **ABCs enforce nominal inheritance contracts; Protocols validate structural method signatures without inheritance coupling.**
"""),

    md_cell("""---
## 3. Code-Reading & Prediction Section
"""),

    # Code Reading 2.1
    md_cell("""### Code-Reading 2.1 — Descriptor Lookup Shadowing
*Predict what will be printed:*
"""),

    code_cell("""class CachedProperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = self.func(instance)
        # Store directly in instance __dict__ to cache!
        instance.__dict__[self.func.__name__] = val
        return val

class DataStore:
    def __init__(self, items):
        self.items = items

    @CachedProperty
    def total(self):
        print("[Computing expensive sum...]")
        return sum(self.items)

ds = DataStore([10, 20, 30])
print("First access: ", ds.total)
print("Second access:", ds.total)
"""),

    md_cell("""**Mechanism**: `CachedProperty` is a **Non-Data Descriptor** (it defines only `__get__`). On the first access, it computes the sum and populates `instance.__dict__['total']`. On subsequent accesses, CPython's attribute lookup checks `instance.__dict__` before non-data descriptors, returning the cached integer directly without re-invoking `total()`!
"""),

    md_cell("""---
## 4. Runtime Inspection Section

We inspect live class MROs, descriptor attributes, and namespace dictionaries.
"""),

    code_cell("""import inspect

class Example:
    @property
    def field(self):
        return 42

ex = Example()

# 1. Inspect class __dict__ vs instance __dict__
print("Class field type:", type(Example.__dict__["field"]))
print("Instance dict:   ", ex.__dict__)

# 2. Query descriptors directly via class dict
descriptor = Example.__dict__["field"]
print("Is descriptor data descriptor?", hasattr(descriptor, "__set__"))
print("Descriptor __get__ directly:", descriptor.__get__(ex, Example))
"""),

    md_cell("""---
### Chapter 2 Lab Complete!
You now have working experimental proof for Python's iteration protocols, generator frame suspension, object lifecycle, MRO C3 linearization, descriptors, context management, and structural typing.
""")
]

nb = make_notebook(cells)
validate_and_save(nb, "f:/notebook/libaray_fluency/02_Python_Data_Model_Protocols_Lab.ipynb")
