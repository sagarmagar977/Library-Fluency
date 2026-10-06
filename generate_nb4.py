"""
Generates 04_Library_Composition_Architecture_Lab.ipynb
"""
from build_notebook_helper import make_notebook, md_cell, code_cell, validate_and_save

cells = [
    md_cell("""# 04 — Library Composition & Architecture Patterns Laboratory

## 0. Notebook Overview

* **Chapter Correlation**: Chapter 4 — Metaprogramming, Class Generation & Architecture Patterns
* **Purpose**: Provide an executable workbench to master Domain-Driven Design (DDD), Dependency Inversion, Ports & Adapters (Hexagonal Architecture), Repository, Service Layer, and Unit of Work (UoW) patterns using 100% pure Python standard library code without external framework dependencies (no Django, FastAPI, or SQLAlchemy required).
* **Prerequisites**: Working knowledge of Python OOP, context managers, and dataclasses.
* **Python Version**: Python 3.10+ (tested on Python 3.14).
* **Required Libraries**: Standard library only (`dataclasses`, `abc`, `typing`, `uuid`).
* **Source Attribution Policy**:
  * `[SOURCE-DERIVED]`: Adapted from *Architecture Patterns with Python* (Percival & Gregory) — Chapters on Domain Modeling, Repository, Service Layer, and Unit of Work.
  * `[SOURCE-ADAPTED]`: Simplified metaprogramming recipes from *Effective Python* and *Python Cookbook (3rd Ed)*.
  * `[ORIGINAL LAB EXPERIMENT]`: Complete cohesive architectural spike combining all layers in pure Python.
"""),

    md_cell("""## 1. Mental Model Map

```text
Ports & Adapters (Hexagonal Architecture) Call Flow:
Web / CLI / Test Entry Point
       │
       ▼ (Calls Use Case with DTOs)
Service Layer (Use Case Orchestrator)
       │
       ├─► Enters Unit of Work (Context Manager for Transaction Boundary)
       │     │
       │     ├─► Loads Domain Aggregate via Repository Port
       │     │
       │     ▼
       │   Domain Aggregate Root (Executes Pure Business Logic & Invariants)
       │     │
       │     ├─► Mutates Pure Domain Entities & Value Objects
       │     └─► Emits Domain Events
       │
       └─► Commits Unit of Work (Atomic State Persistence)
```
"""),

    md_cell("""---
## 2. Core Architecture Experiments
"""),

    # Experiment 4.1
    md_cell("""### Experiment 4.1 — Subclass Validation & Registration with `__init_subclass__`
*Category: [SOURCE-ADAPTED - Effective Python Item 48]*

#### What are we investigating?
We demonstrate how `__init_subclass__` (PEP 487) replaces complex metaclasses for plugin registration and interface enforcement, avoiding metaclass conflict errors.

#### Mental Model
When a class inherits from a base defining `__init_subclass__`, Python invokes that hook automatically at class creation time.

#### Code
We build an automatic plugin registry that validates required attributes at definition time.
"""),

    code_cell("""class PluginBase:
    registry = {}

    def __init_subclass__(cls, plugin_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name is None:
            raise TypeError(f"Class {cls.__name__} must specify 'plugin_name'")
        
        # Enforce interface requirement
        if not hasattr(cls, "execute"):
            raise TypeError(f"Plugin {cls.__name__} must implement 'execute()'")
            
        cls.registry[plugin_name] = cls
        print(f"Registered plugin '{plugin_name}' -> {cls.__name__}")

# Subclasses register automatically at definition time!
class JsonExporter(PluginBase, plugin_name="json"):
    def execute(self, data):
        return f"JSON: {data}"

class CsvExporter(PluginBase, plugin_name="csv"):
    def execute(self, data):
        return f"CSV: {data}"

print("\\nActive Plugin Registry:", PluginBase.registry)
"""),

    md_cell("""#### Observe
The classes were registered into `PluginBase.registry` immediately upon module definition without manual dictionary insertion or metaclass complexity.

#### Recall Rule
> **Use `__init_subclass__` for subclass validation and automatic registration without metaclass MRO conflicts.**
"""),

    # Experiment 4.2
    md_cell("""---
### Experiment 4.2 — Pure Domain Models: Entities vs Value Objects
*Category: [SOURCE-DERIVED - Architecture Patterns with Python Ch 1]*

#### What are we investigating?
We implement pure Python domain models isolated from database concerns, strictly distinguishing **Value Objects** (immutable, equality based on values) from **Entities** (identity-tracked, equality based on persistent `id`).

#### Mental Model
- **Value Object**: `@dataclass(frozen=True)`. Equal if all fields match. No independent identity. (e.g. `Money(10, "USD") == Money(10, "USD")`).
- **Entity**: Has an explicit `id`. Equal if `self.id == other.id`, even if other attributes mutate over time.

#### Code
We construct both types and observe equality and hashing behavior.
"""),

    code_cell("""from dataclasses import dataclass
from typing import List

# 1. Pure Value Object (Immutable, attribute equality)
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

m1 = Money(100.0, "USD")
m2 = Money(100.0, "USD")
print(f"Value Objects Equal? {m1 == m2} (Attributes match)")
print(f"Value Object Hashable? {hash(m1) == hash(m2)}")

# 2. Pure Domain Entity (Identity equality)
class OrderLine:
    def __init__(self, line_id: str, sku: str, quantity: int):
        self.line_id = line_id
        self.sku = sku
        self.quantity = quantity

    def __eq__(self, other):
        if not isinstance(other, OrderLine):
            return False
        return self.line_id == other.line_id

    def __hash__(self):
        return hash(self.line_id)

line1 = OrderLine("L-001", "SKU-RED-CHAIR", 2)
line2 = OrderLine("L-001", "SKU-RED-CHAIR", 5)  # Different quantity!

print(f"\\nEntities Equal? {line1 == line2} (IDs match despite different quantity!)")
"""),

    md_cell("""#### Recall Rule
> **Value Objects are defined and compared by their values; Entities are defined and compared by persistent identity.**
"""),

    # Experiment 4.3
    md_cell("""---
### Experiment 4.3 — The Repository Pattern (Storage Abstraction)
*Category: [SOURCE-DERIVED - Architecture Patterns with Python Ch 2]*

#### What are we investigating?
We build an abstract repository port (`AbstractRepository`) and an in-memory test adapter (`FakeRepository`) that presents database storage as a simple Python collection.

#### Code
We define the abstract port and implement an in-memory collection.
"""),

    code_cell("""import abc

# Port (Abstract Interface)
class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, order_line: OrderLine) -> None:
        pass

    @abc.abstractmethod
    def get(self, line_id: str) -> OrderLine:
        pass

# Adapter (In-Memory Fake for ultra-fast unit testing)
class FakeRepository(AbstractRepository):
    def __init__(self, initial_lines=None):
        self._lines = set(initial_lines or [])

    def add(self, order_line: OrderLine) -> None:
        self._lines.add(order_line)

    def get(self, line_id: str) -> OrderLine:
        for line in self._lines:
            if line.line_id == line_id:
                return line
        raise KeyError(f"OrderLine {line_id} not found")

# Test in-memory repository
repo = FakeRepository()
repo.add(OrderLine("L-100", "DESK-OAK", 1))
fetched = repo.get("L-100")
print("Fetched from FakeRepository:", fetched.line_id, fetched.sku)
"""),

    md_cell("""#### Recall Rule
> **Repositories abstract data access, allowing domain logic to treat persistent storage like an in-memory collection.**
"""),

    # Experiment 4.4
    md_cell("""---
### Experiment 4.4 — The Unit of Work (UoW) Pattern
*Category: [SOURCE-DERIVED - Architecture Patterns with Python Ch 6]*

#### What are we investigating?
We implement a Unit of Work context manager that maintains transactional consistency across repositories, ensuring atomic commits and automatic rollbacks on errors.

#### Code
We build a working in-memory Unit of Work context manager.
"""),

    code_cell("""class AbstractUnitOfWork(abc.ABC):
    lines: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.lines = FakeRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True
        print(" -> UoW: Committed successfully.")

    def rollback(self):
        self.rolled_back = True
        print(" -> UoW: Rolled back changes due to exception.")

# Test 1: Successful Transaction
print("=== Transaction 1: Success ===")
with FakeUnitOfWork() as uow:
    uow.lines.add(OrderLine("L-201", "MONITOR-4K", 1))
print("Committed:", uow.committed)

# Test 2: Failed Transaction (Auto-Rollback)
print("\\n=== Transaction 2: Error Rollback ===")
try:
    with FakeUnitOfWork() as uow_fail:
        uow_fail.lines.add(OrderLine("L-202", "KEYBOARD-MECH", 1))
        raise RuntimeError("Payment gateway failed!")
except RuntimeError:
    print("Caught application error outside context.")
print("Rolled Back:", uow_fail.rolled_back)
"""),

    md_cell("""#### Recall Rule
> **Unit of Work enforces atomic transactions via context manager semantics (`__enter__` / `__exit__`).**
"""),

    # Experiment 4.5
    md_cell("""---
### Experiment 4.5 — Complete Cohesive Architectural Spike
*Category: [ORIGINAL LAB EXPERIMENT]*

#### What are we investigating?
We assemble all DDD and Hexagonal architecture components into a unified, 35-line end-to-end working system: Entity + Value Object + Repository + Unit of Work + Service Layer.

#### Code
"""),

    code_cell("""# 1. Pure Domain Model
@dataclass(frozen=True)
class Price(Money):
    pass

class Product:
    def __init__(self, sku: str, price: Price):
        self.sku = sku
        self.price = price
        self.inventory = 0

    def restock(self, quantity: int):
        self.inventory += quantity

# 2. Storage Port & Adapter
class ProductRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, sku: str) -> Product: pass
    @abc.abstractmethod
    def add(self, p: Product) -> None: pass

class InMemoryProductRepo(ProductRepository):
    def __init__(self): self._db = {}
    def get(self, sku: str) -> Product: return self._db[sku]
    def add(self, p: Product) -> None: self._db[p.sku] = p

# 3. Unit of Work
class ProductUoW:
    def __init__(self, repo): self.products = repo
    def __enter__(self): return self
    def __exit__(self, exc, val, tb): pass

# 4. Service Layer (Use Case Orchestration)
def restock_product_service(sku: str, qty: int, uow: ProductUoW):
    with uow:
        product = uow.products.get(sku)
        product.restock(qty)
        return product.inventory

# === Run the Complete System ===
repo = InMemoryProductRepo()
repo.add(Product("LAPTOP-PRO", Price(1200.0, "USD")))
uow = ProductUoW(repo)

new_stock = restock_product_service("LAPTOP-PRO", 5, uow)
print(f"Service Execution Success! New inventory for LAPTOP-PRO: {new_stock}")
"""),

    md_cell("""#### Observe
The Service Layer coordinates business logic without knowing anything about a database, web framework, or UI controller. The entire architecture is decoupled, testable in-memory, and modular.

#### Recall Rule
> **Core domain models remain pure; repositories abstract storage; Unit of Work enforces boundaries; the Service Layer orchestrates use cases.**
"""),

    md_cell("""---
## 3. Code-Reading & Prediction Section
"""),

    # Code Reading 4.1
    md_cell("""### Code-Reading 4.1 — Entity Identity Comparison Under Mutation
*Predict the output:*
"""),

    code_cell("""e1 = OrderLine("ID-1", "WIDGET", 10)
e2 = OrderLine("ID-1", "GADGET", 99)

print("e1 == e2: ", e1 == e2)
print("e1 is e2: ", e1 is e2)
print("Set size: ", len({e1, e2}))
"""),

    md_cell("""**Mechanism**: Because `OrderLine` implemented `__eq__` and `__hash__` based exclusively on `line_id`, `e1 == e2` is `True`. In a Python `set`, `e2` collides with `e1`, resulting in a set of size 1 despite distinct memory addresses.
"""),

    md_cell("""---
## 4. Runtime Inspection Section

We inspect registered classes dynamically using `__subclasses__()`.
"""),

    code_cell("""print("Subclasses of PluginBase:", [cls.__name__ for cls in PluginBase.__subclasses__()])"""),

    md_cell("""---
### Chapter 4 Lab Complete!
You now have working experimental proof of clean architecture, domain modeling, repositories, Unit of Work, and service layer composition in pure Python.
""")
]

nb = make_notebook(cells)
validate_and_save(nb, "f:/notebook/libaray_fluency/04_Library_Composition_Architecture_Lab.ipynb")
