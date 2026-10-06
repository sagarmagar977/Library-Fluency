### **CHAPTER 2 — THE PYTHON DATA MODEL & OBJECT PROTOCOLS**

> **Central Mental Model**: Python objects participate in protocols. For every protocol, CPython executes a fixed sequence: **What Python asks → What method responds → What happens → Why it matters.**

---

### **2.1. The Iteration Protocol & Generator Mechanics**

**CONCEPT**  
Iteration in Python is decoupled from specific sequence lengths or indexing. Any object can become an iterable or an iterator by implementing the iteration protocol.

```
+-------------------------------------------------------------------------+
| STEP 1: iter(obj) invoked (by 'for', comprehensions, or unpacking)      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| STEP 2: Does obj define __iter__()?                                     |
|   - YES: Calls obj.__iter__() -> Must return an Iterator object         |
|   - NO:  Falls back to __getitem__(index) starting at index 0           |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| STEP 3: Repeatedly call next(iterator) -> invokes iterator.__next__()    |
|   - Yields next value on each call                                      |
|   - Raises StopIteration when sequence is exhausted                     |
+-------------------------------------------------------------------------+
```

**PROTOCOL BREAKDOWN**  
- **What Python Asks**: `iter(obj)` when entering `for` loops, comprehensions, or unpacking statements.
- **What Method Responds**: `obj.__iter__()`. If absent, Python falls back to `obj.__getitem__(i)` with sequential integer indices `0, 1, 2...` until `IndexError` is raised.
- **What Happens**: `obj.__iter__()` returns an **iterator** object. Python repeatedly invokes `next(iterator)` (which calls `iterator.__next__()`) to retrieve values.
- **Termination**: When data is exhausted, `__next__()` raises a `StopIteration` exception, which the calling construct catches to terminate cleanly.

**GENERATORS & LAZY EVALUATION**  
- Any function containing the `yield` keyword is compiled into a **generator function**. Calling it returns a **generator-iterator** object without executing the function body immediately.
- Execution suspends at `yield <expr>`, freezing the stack frame state (`PyFrameObject`) and returning the yielded value to the caller.
- **`yield from <expr>` Sub-generator Delegation**: Automatically opens a bidirectional channel to an inner iterable. It forwards yielded values, exceptions via `.throw()`, cleanup via `.close()`, and captures the sub-generator’s `return <expr>` value via `StopIteration.value`.

**CHEAT-CODE RULES**  
> **Iterables implement `__iter__()` returning an iterator; Iterators implement `__next__()` and `__iter__()` returning `self`.**  
> **Generators are state machines that pause evaluation and preserve stack frames across `yield` points.**

**KEYWORD MEMORY ANCHOR**  
`iter() → __iter__() → Iterator Object → __next__() → StopIteration`

---

### **2.2. Object Creation, Instantiation & Lifecycle (`__new__` vs `__init__`)**

**CONCEPT**  
Instantiation is a two-phase process: instance **allocation** (`__new__`) followed by instance **initialization** (`__init__`).

```
Call: Class(*args, **kwargs)
  │
  ├── 1. Allocation Phase: instance = Class.__new__(Class, *args, **kwargs)
  │      └── Returns a newly constructed raw object instance.
  │
  └── 2. Initializer Check:
         ├── IF isinstance(instance, Class):
         │      Class.__init__(instance, *args, **kwargs)  [Returns None]
         └── ELSE:
                Skip __init__ call; return instance as-is.
```

**KEY TECHNICAL RULES**  
1. **`__new__(cls, *args, **kwargs)`**:
   - Static method (implicit) responsible for creating and returning a new object instance in memory.
   - Must invoke `super().__new__(cls)` to delegate allocation to C-level base types.
   - Crucial for controlling instance creation: implementing Singletons, immutable type customization (subclassing `tuple` or `str`), instance interning, and caching.
2. **`__init__(self, *args, **kwargs)`**:
   - Instance method called *after* `__new__` has returned an instance of `cls`.
   - Customizes the instance state (`self.attr = val`) and **must return `None`**.
3. **Destruction & Garbage Collection (`__del__`)**:
   - `__del__(self)` is invoked when an instance's reference count drops to zero.
   - It is an object finalizer, not a C++ style deterministic destructor. Delayed execution occurs if cyclic references exist unless handled by CPython's cyclic garbage collector.
   - Resource cleanup should be placed in explicit `close()` or context managers rather than relying on `__del__`.

**CHEAT-CODE RULES**  
> **`__new__` allocates and returns the object; `__init__` populates its attributes and returns `None`.**  
> **`__init__` only fires automatically if `__new__` returns an instance of the class being called.**

---

### **2.3. Inheritance, MRO & C3 Linearization Mechanics**

**CONCEPT**  
Python resolves attribute lookups across complex or multiple inheritance hierarchies by linearizing classes into a flat, deterministic sequence called the **Method Resolution Order (MRO)**.

**KEY TECHNICAL RULES**  
1. **C3 Linearization Algorithm**:
   CPython calculates `Class.__mro__` at class definition time by merging the parent MROs while enforcing three strict constraints:
   - **Child First**: A class always appears before its parent classes.
   - **Local Precedence**: Parent classes listed in a class definition `class Sub(A, B):` maintain their left-to-right order.
   - **Monotonicity**: If class `A` precedes class `B` in the MRO of any parent, `A` must precede `B` in all subclass MROs. Hierarchies violating this throw a `TypeError` at class creation.
2. **Cooperative Delegation (`super()`)**:
   - `super().method(*args)` does **not** simply call the parent class method.
   - It searches the instance's MRO starting **immediately after** the class in which the current `super()` call resides.
   - In multiple inheritance (e.g., Mixin patterns), `super()` routes calls horizontally across peer classes before ascending to common ancestors.

```
Diamond Hierarchy MRO Resolution:
      Object
        |
       Base
      /    \
     A      B
      \    /
        C

C.__mro__ -> (C, A, B, Base, object)
super() in A delegates to B, NOT Base!
```

**CHEAT-CODE RULE**  
> **`super()` delegates to the *next class in the caller instance’s runtime MRO*, not to the static syntactic parent.**

---

### **2.4. Attribute Access & Descriptor Protocol**

**CONCEPT**  
Attribute access (`obj.attr`) is orchestrated through Python's descriptor protocol. Descriptors power properties, bound methods, `@classmethod`, `@staticmethod`, and `__slots__`.

**PROTOCOL BREAKDOWN**  
- **Descriptor Interface**: Any class defining at least one of `__get__`, `__set__`, or `__delete__`.
  - `__get__(self, instance, owner=None)`: Invoked on retrieval. When accessed via class `Owner.attr`, `instance` is `None`.
  - `__set__(self, instance, value)`: Invoked on attribute assignment `obj.attr = val`.
  - `__delete__(self, instance)`: Invoked on attribute deletion `del obj.attr`.
  - `__set_name__(self, owner, name)`: Hook invoked at class creation time, binding the attribute name string to the descriptor instance.

**DATA VS. NON-DATA DESCRIPTORS**  
- **Data Descriptors**: Define `__set__` and/or `__delete__` (alongside `__get__`).  
  *Precedence*: **Overrides entries in the instance `__dict__`**. Example: `@property`.
- **Non-Data Descriptors**: Define only `__get__`.  
  *Precedence*: **Overridden by entries in the instance `__dict__`**. Examples: Python functions/methods, `@classmethod`, `@staticmethod`, lazy properties.

**ATTRIBUTE LOOKUP CHAIN (`obj.attr`)**  
```
1. Check type(obj) and its MRO for a DATA DESCRIPTOR matching 'attr'.
   ├── Found -> Invoke DataDescriptor.__get__(obj, type(obj))
   └── Not Found -> Proceed to Step 2.

2. Check instance dictionary: obj.__dict__['attr'].
   ├── Found -> Return value directly.
   └── Not Found -> Proceed to Step 3.

3. Check type(obj) and its MRO for a NON-DATA DESCRIPTOR or Class Attribute.
   ├── Found Non-Data Descriptor -> Invoke NonDataDescriptor.__get__(obj, type(obj))
   ├── Found Normal Attribute -> Return class attribute value.
   └── Not Found -> Proceed to Step 4.

4. Invoke type(obj).__getattr__(obj, 'attr') if defined on class.
   ├── Returns computed value or raises AttributeError.
   └── Not Defined -> Raise AttributeError.
```

**CHEAT-CODE RULES**  
> **Data Descriptors (`__set__`) take precedence over instance `__dict__`; Non-Data Descriptors (`__get__` only) yield to instance `__dict__`.**  
> **`__getattribute__` executes on *every* attribute access; `__getattr__` executes *only* when the lookup chain fails.**

---

### **2.5. Context Management Protocol (`with` & `contextlib`)**

**CONCEPT**  
Context managers encapsulate resource setup and cleanup around a block of code, guaranteeing execution regardless of exceptions or early control flow exits.

**PROTOCOL BREAKDOWN**  
- **What Python Asks**: `with cm as var:`.
- **What Method Responds**:
  1. `cm.__enter__()`: Invoked on block entry. Its return value binds to `var` in the `as var` clause.
  2. `cm.__exit__(exc_type, exc_val, exc_tb)`: Invoked on block exit.
- **Exception Handling Mechanics**:
  - If the `with` block exits cleanly, `__exit__` receives `(None, None, None)`.
  - If an exception occurs, `__exit__` receives exception details (`sys.exc_info()`).
  - **Suppression Rule**: If `__exit__` returns a **truthy value** (`True`), the pending exception is silenced, and program execution continues after the `with` block. Returning `False` or `None` re-raises the exception.

**`@contextlib.contextmanager` MECHANICS**  
Decorating a generator function converts it into a context manager:
```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    # Setup Phase (__enter__)
    res = acquire_resource()
    try:
        yield res  # Value bound to 'as var'
    except Exception as e:
        # Handle or re-raise error inside generator
        raise e
    finally:
        # Cleanup Phase (__exit__)
        release_resource(res)
```

---

### **2.6. Nominal vs. Structural Typing (ABCs vs. `typing.Protocol`)**

**CONCEPT**  
Python supports both explicit type hierarchies (**Nominal Subtyping**) and static structural duck typing (**Structural Subtyping**).

**COMPARISON MATRIX**  
- **Abstract Base Classes (`collections.abc`, `abc.ABCMeta`) — Nominal**:
  - Requires explicit class inheritance (`class MyList(collections.abc.MutableSequence)`) or explicit runtime registration (`ABC.register(CustomClass)`).
  - Enforces interface compliance at instantiation time by blocking instance creation if abstract methods (`@abstractmethod`) remain unimplemented.
- **Protocol Classes (`typing.Protocol`) — Structural**:
  - Defines static interface contracts without requiring explicit inheritance ("static duck typing").
  - Checked at static analysis time (mypy); runtime validation achieved via `@typing.runtime_checkable` checking for method existence via `isinstance()`.

---

### **2.7. Chapter 2 Summary & Rapid Recall**

```
+---------------------+-----------------------------------------------------------------------------------------+
| Protocol / Method   | Core Trigger & Execution Rule                                                           |
+---------------------+-----------------------------------------------------------------------------------------+
| __iter__ / __next__ | Iteration protocol; iter() calls __iter__(), next() calls __next__() until StopIteration |
| yield / yield from  | Suspends frame state; yield from delegates bidirectionally to inner sub-generator       |
| __new__ vs __init__ | __new__ allocates/returns object; __init__ populates state and must return None         |
| C3 Linearization    | Calculates MRO hierarchy enforcing Child First, Local Precedence, and Monotonicity      |
| super()             | Delegates attribute lookup to the next class in the caller instance's dynamic MRO       |
| Data Descriptor     | Implements __set__/__delete__; takes lookup precedence OVER instance __dict__          |
| Non-Data Descriptor | Implements __get__ only; yields lookup precedence TO instance __dict__                  |
| __getattr__         | Fallback hook called ONLY when normal attribute lookup chain fails                      |
| __enter__/__exit__  | Context management; __exit__ returning True suppresses caught exception                 |
| typing.Protocol     | Structural interface contract checked statically without explicit class inheritance     |
+---------------------+-----------------------------------------------------------------------------------------+
```

---

🎯 **Ready to continue?** Say **"next"** or **"go to Chapter 3"** to proceed to **Chapter 3 — Library Literacy, Inspection & Concurrency** (covering runtime interrogation, `inspect`, dynamic imports via `importlib`, threading, GIL mechanics, multiprocessing, and `asyncio` event loops).