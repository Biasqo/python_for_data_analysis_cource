# Lesson 4 — Advanced Python: Sugar, Typing, Paradigms
**Block 4 — Classes & Functions | Duration: 90 minutes | Level: Intermediate/Advanced**

---

## Learning Objectives

By the end of this lesson, students will be able to:
1. Apply Python's syntactic sugar features (`walrus`, unpacking, decorators) to write concise, readable code.
2. Use `typing` annotations and `@dataclass` to make data-handling code self-documenting.
3. Solve the same problem in procedural, functional, and OOP styles and articulate the trade-offs.
4. Write and use custom context managers and exception hierarchies.

---

## Minute-by-Minute Plan

### 0–25 | Syntactic Sugar

#### Walrus operator (`:=`)
```python
# Without walrus — redundant computation or variable
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ❌ Verbose
filtered = [x for x in data if x > 5]
if len(filtered) > 3:
    print(f"Found {len(filtered)} items")   # computed twice

# ✅ Walrus — assign inside expression
if (n := len([x for x in data if x > 5])) > 3:
    print(f"Found {n} items")   # n already bound

# Walrus in while loop — common pattern for streaming reads
import io
source = io.StringIO("line1\nline2\nline3")
while chunk := source.readline():
    print(chunk.strip())
```

#### Unpacking
```python
# Basic unpacking
first, *rest = [10, 20, 30, 40, 50]
print(first)  # 10
print(rest)   # [20, 30, 40, 50]

# Swap without temp variable
a, b = 1, 2
a, b = b, a

# Unpack in for
records = [("Alice", 85), ("Bob", 92), ("Carol", 78)]
for name, score in records:
    print(f"{name}: {score}")

# Dict unpacking / merge (Python 3.9+)
defaults = {"timeout": 30, "retries": 3}
overrides = {"retries": 5, "verbose": True}
config = {**defaults, **overrides}
print(config)  # {'timeout': 30, 'retries': 5, 'verbose': True}
```

#### `*args` and `**kwargs`
```python
def summarize(*values, label="Summary", precision=2):
    total = sum(values)
    avg = total / len(values)
    return f"{label}: total={total:.{precision}f}, avg={avg:.{precision}f}"

print(summarize(10, 20, 30, label="Q1 Revenue"))
# Q1 Revenue: total=60.00, avg=20.00

# Forwarding kwargs — useful in wrappers
def log_and_call(func, **kwargs):
    print(f"Calling {func.__name__} with {kwargs}")
    return func(**kwargs)
```

#### Decorators
```python
import time
import functools

# Simple timer decorator
def timer(func):
    @functools.wraps(func)  # preserve original function name/docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def load_data(path: str) -> list:
    time.sleep(0.1)  # simulate I/O
    return []

load_data("data.csv")  # load_data took 0.1003s

# Decorator with arguments
def retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
            raise RuntimeError(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator

@retry(max_attempts=3)
def fetch_data(url: str):
    raise ConnectionError("Network down")  # simulate failure
```

---

### 25–45 | Typing

#### Basic annotations
```python
from typing import Optional, Union, Literal
from collections.abc import Sequence

# Simple annotations (Python 3.10+ style uses | instead of Union)
def compute_tax(amount: float, rate: float = 0.20) -> float:
    return amount * rate

# Optional — value or None
def find_customer(customer_id: int) -> Optional[dict]:
    db = {1: {"name": "Alice"}}
    return db.get(customer_id)   # returns dict or None

# Union (Python 3.10+: float | str)
def format_amount(value: Union[float, str]) -> str:
    return f"${float(value):,.2f}"

# Literal — constrained string values
Status = Literal["pending", "approved", "rejected"]
def update_status(order_id: int, status: Status) -> None:
    print(f"Order {order_id} → {status}")

# Sequence — accepts list, tuple, etc.
def average(values: Sequence[float]) -> float:
    return sum(values) / len(values)
```

#### `@dataclass` — structured data without boilerplate
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Transaction:
    id: int
    category: str
    amount: float
    currency: str = "USD"
    tags: list[str] = field(default_factory=list)   # safe mutable default
    note: Optional[str] = None

    @property
    def amount_eur(self) -> float:
        rates = {"USD": 0.92, "GBP": 1.15}
        return self.amount * rates.get(self.currency, 1.0)

t = Transaction(id=1, category="electronics", amount=500.0)
print(t)                 # Transaction(id=1, category='electronics', ...)
print(t.amount_eur)      # 460.0
print(t == Transaction(id=1, category="electronics", amount=500.0))  # True (auto __eq__)
```

**Why dataclass over plain dict?**
- IDE autocomplete on fields.
- Type checking with `mypy`.
- Auto-generated `__repr__`, `__eq__`.
- No `d["field"]` vs `d.field` confusion.

---

### 45–70 | Programming Paradigms

**Demo task:** Compute total sales per category from a list of transactions.

```python
transactions = [
    {"category": "electronics", "amount": 500},
    {"category": "food",        "amount": 30},
    {"category": "electronics", "amount": 200},
    {"category": "food",        "amount": 45},
    {"category": "clothing",    "amount": 120},
]
```

#### 1. Procedural style
```python
# Explicit, imperative, easy to debug step-by-step
def compute_totals_procedural(transactions):
    totals = {}
    for t in transactions:
        cat = t["category"]
        if cat not in totals:
            totals[cat] = 0.0
        totals[cat] += t["amount"]
    return totals

print(compute_totals_procedural(transactions))
# {'electronics': 700.0, 'food': 75.0, 'clothing': 120.0}
```

#### 2. Functional style
```python
from functools import reduce

def compute_totals_functional(transactions):
    def reducer(acc, t):
        cat = t["category"]
        return {**acc, cat: acc.get(cat, 0) + t["amount"]}

    return reduce(reducer, transactions, {})

# Or with dict comprehension + groupby
from itertools import groupby

def compute_totals_groupby(transactions):
    sorted_txns = sorted(transactions, key=lambda t: t["category"])
    return {
        cat: sum(t["amount"] for t in group)
        for cat, group in groupby(sorted_txns, key=lambda t: t["category"])
    }

print(compute_totals_functional(transactions))
```

#### 3. OOP style
```python
from collections import defaultdict

class SalesAggregator:
    def __init__(self):
        self._totals: dict[str, float] = defaultdict(float)
        self._counts: dict[str, int] = defaultdict(int)

    def process(self, transaction: dict) -> "SalesAggregator":
        cat = transaction["category"]
        self._totals[cat] += transaction["amount"]
        self._counts[cat] += 1
        return self   # fluent interface for chaining

    def summary(self) -> dict:
        return {
            cat: {"total": total, "count": self._counts[cat], "avg": total / self._counts[cat]}
            for cat, total in self._totals.items()
        }

agg = SalesAggregator()
for t in transactions:
    agg.process(t)
print(agg.summary())
```

**Discussion:** Which scales best when:
- You add a new field (currency) → OOP cleanest.
- You need to parallelize → functional cleanest (immutable).
- You need to debug line-by-line → procedural.

---

### 70–85 | Exceptions and Context Managers

#### Exception hierarchy
```python
# Custom exceptions — give operators actionable error messages
class DataPipelineError(Exception):
    """Base for all pipeline errors."""

class MissingFieldError(DataPipelineError):
    def __init__(self, field: str, row_id):
        self.field = field
        self.row_id = row_id
        super().__init__(f"Row {row_id}: missing required field '{field}'")

class InvalidAmountError(DataPipelineError):
    pass

# Usage with try/except/else/finally
def parse_transaction(row: dict) -> dict:
    try:
        amount = float(row["amount"])
        if amount < 0:
            raise InvalidAmountError(f"Negative amount: {amount}")
    except KeyError:
        raise MissingFieldError("amount", row.get("id", "?"))
    except ValueError:
        raise InvalidAmountError(f"Non-numeric amount: {row['amount']!r}")
    else:
        # runs only if no exception
        return {"category": row["category"], "amount": amount}
    finally:
        # always runs — use for cleanup / logging
        pass   # e.g., close DB connection
```

#### Context managers
```python
# Class-based context manager
class Timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False   # don't suppress exceptions

with Timer() as t:
    result = sum(range(1_000_000))
print(f"Sum: {result}")

# Generator-based (simpler)
from contextlib import contextmanager

@contextmanager
def managed_connection(path):
    conn = open(path)
    try:
        yield conn
    finally:
        conn.close()
        print("Connection closed")

with managed_connection("data.csv") as f:
    print(f.readline())
```

---

### 85–90 | Homework Introduction

**Assignment:** Implement a `TransactionProcessor` class with:
- `@dataclass` for `Transaction`.
- A `process_batch(transactions)` method using your chosen paradigm.
- A `@retry(3)` decorator on the data-loading function.
- Custom exceptions for missing fields and invalid amounts.

---

## Check for Understanding

**5 questions (minute 83):**

1. What does `@functools.wraps(func)` do inside a decorator?
   > Copies the original function's `__name__`, `__doc__`, etc. to the wrapper, so debugging and introspection see the original function, not `wrapper`.

2. What is the output?
   ```python
   a, *b, c = [1, 2, 3, 4, 5]
   print(b)
   ```
   > `[2, 3, 4]`

3. Why use `field(default_factory=list)` in a `@dataclass` instead of `tags: list = []`?
   > A mutable default (`[]`) would be shared across all instances (same bug as mutable function defaults). `default_factory` creates a fresh list for each instance.

4. What is the difference between `else` and `finally` in a `try` block?
   > `else` runs only when no exception was raised; `finally` always runs, even after an exception or `return`.

5. Which paradigm (procedural/functional/OOP) would you choose for a one-off exploratory script, and why?
   > Procedural — easiest to write quickly, straightforward to debug, no overhead of classes or functional composition.