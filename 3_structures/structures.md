# Lesson 3 — Python Data Structures
**Block 3 — Data Structures | Duration: 90 minutes | Level: Intermediate/Advanced**

---

## Learning Objectives

By the end of this lesson, students will be able to:
1. Choose the right built-in structure (`list`, `tuple`, `dict`, `set`) based on operation complexity and semantic intent.
2. Identify and fix aliasing bugs caused by shallow copies of mutable structures.
3. Use `collections` module types (`Counter`, `defaultdict`, `namedtuple`) to simplify aggregation code.
4. Write readable, performant comprehensions for nested and flat data.

---

## Minute-by-Minute Plan

### 0–25 | list, tuple, dict, set

**Complexity reference table — post this on the screen:**

| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| `list` | O(1) by index | O(n) | O(1) append | O(n) arbitrary | Ordered, mutable |
| `tuple` | O(1) by index | O(n) | — | — | Immutable, hashable |
| `dict` | O(1) by key | O(1) by key | O(1) | O(1) | Ordered (3.7+), mutable |
| `set` | — | O(1) | O(1) | O(1) | Unordered, no duplicates, hashable elements |

#### Practical examples
```python
# list — use for ordered sequences you iterate
prices = [10.5, 20.0, 15.75]
prices.append(8.99)
print(prices[-1])    # 8.99 (last element)

# tuple — use for fixed records (coordinates, DB rows)
point = (52.52, 13.40)  # lat/lon Berlin
# point[0] = 0  ← TypeError: immutable

# dict — use for labeled data / lookup tables
country_gdp = {"Germany": 4.07, "France": 2.78, "Italy": 2.10}
print(country_gdp.get("Spain", 0))  # 0 — safe get with default

# set — use for membership tests and deduplication
categories = {"electronics", "clothing", "food", "clothing"}
print(categories)   # {'electronics', 'clothing', 'food'} — no duplicates

# O(1) lookup vs O(n) — important at scale
large_set = set(range(1_000_000))
large_list = list(range(1_000_000))

# %timeit 999_999 in large_set    → ~50 ns
# %timeit 999_999 in large_list   → ~10 ms  (200x slower)
```

#### Hashability — why it matters for dict keys and set elements
```python
# Hashable (can be dict key / set element)
{1: "ok"}          # int ✓
{(1, 2): "ok"}     # tuple of ints ✓

# Not hashable
# {[1, 2]: "fail"}   # TypeError: unhashable type: 'list'
# {{}: "fail"}       # TypeError: unhashable type: 'dict'

# Rule: only immutable types are hashable
```

---

### 25–45 | Mutability and Identity

#### `is` vs `==`
```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)   # True  — same values
print(a is b)   # False — different objects in memory
print(a is c)   # True  — same object (alias!)

# Danger: modifying c also modifies a
c.append(4)
print(a)  # [1, 2, 3, 4]  ← surprise!
```

#### Shallow vs deep copy
```python
import copy

original = {"name": "Alice", "scores": [90, 85, 78]}

# Shallow copy — top-level is new, nested is shared
shallow = original.copy()
shallow["name"] = "Bob"          # ok — doesn't affect original
shallow["scores"].append(70)     # BUG — mutates original's list too!
print(original["scores"])        # [90, 85, 78, 70]  ← mutated

# Deep copy — fully independent
original = {"name": "Alice", "scores": [90, 85, 78]}
deep = copy.deepcopy(original)
deep["scores"].append(70)
print(original["scores"])        # [90, 85, 78]  ← safe
```

#### Common aliasing trap with nested lists
```python
# ❌ Wrong — all rows point to the same list
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)  # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] ← not what you wanted

# ✅ Correct — each row is an independent list
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print(matrix)  # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

---

### 45–65 | `collections` Module

```python
from collections import Counter, defaultdict, namedtuple, OrderedDict
```

#### Counter
```python
from collections import Counter

transactions = ["electronics", "food", "clothing", "food", "food", "electronics"]

counts = Counter(transactions)
print(counts)                   # Counter({'food': 3, 'electronics': 2, 'clothing': 1})
print(counts.most_common(2))    # [('food', 3), ('electronics', 2)]

# Counter arithmetic
a = Counter(["x", "y", "x"])
b = Counter(["y", "y", "z"])
print(a + b)   # Counter({'y': 3, 'x': 2, 'z': 1})
print(a - b)   # Counter({'x': 2}) — only positive
```

#### defaultdict — avoid `if key in dict` boilerplate
```python
from collections import defaultdict

orders = [
    {"category": "electronics", "amount": 500},
    {"category": "food",        "amount": 30},
    {"category": "electronics", "amount": 200},
    {"category": "food",        "amount": 45},
]

# ❌ Manual approach
totals_manual = {}
for order in orders:
    cat = order["category"]
    if cat not in totals_manual:
        totals_manual[cat] = 0
    totals_manual[cat] += order["amount"]

# ✅ defaultdict
totals = defaultdict(float)
for order in orders:
    totals[order["category"]] += order["amount"]

print(dict(totals))  # {'electronics': 700.0, 'food': 75.0}

# defaultdict(list) — grouping
by_category = defaultdict(list)
for order in orders:
    by_category[order["category"]].append(order["amount"])

print(dict(by_category))
# {'electronics': [500, 200], 'food': [30, 45]}
```

#### namedtuple — readable records without a full class
```python
from collections import namedtuple

Transaction = namedtuple("Transaction", ["id", "category", "amount", "currency"])

t = Transaction(id=1, category="electronics", amount=500.0, currency="USD")
print(t.amount)       # 500.0 — attribute access
print(t[2])           # 500.0 — also index-accessible
print(t._asdict())    # OrderedDict for easy JSON serialization
```

---

### 65–85 | Comprehensions and Nested Structures

#### Comprehension syntax
```python
# List comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# Dict comprehension
prices = {"apple": 1.2, "banana": 0.5, "cherry": 3.0}
expensive = {k: v for k, v in prices.items() if v > 1.0}
# {'apple': 1.2, 'cherry': 3.0}

# Set comprehension
categories = {"food", "food", "tech", "food", "tech"}  # ← dedup on creation

# Generator expression (lazy — no list built in memory)
total = sum(x**2 for x in range(1_000_000))  # memory-efficient
```

#### Processing JSON-like nested data (realistic scenario)
```python
# Typical API response — list of dicts with nested fields
orders = [
    {"id": 1, "customer": {"country": "DE"}, "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 1}]},
    {"id": 2, "customer": {"country": "FR"}, "items": [{"sku": "A1", "qty": 1}]},
    {"id": 3, "customer": {"country": "DE"}, "items": [{"sku": "C3", "qty": 5}]},
]

# 1. Flatten all items
all_items = [item for order in orders for item in order["items"]]
print(all_items)
# [{'sku': 'A1', 'qty': 2}, {'sku': 'B2', 'qty': 1}, {'sku': 'A1', 'qty': 1}, {'sku': 'C3', 'qty': 5}]

# 2. Total quantity per SKU
qty_per_sku = Counter()
for item in all_items:
    qty_per_sku[item["sku"]] += item["qty"]
print(dict(qty_per_sku))  # {'A1': 3, 'B2': 1, 'C3': 5}

# 3. Orders per country
orders_by_country = defaultdict(list)
for order in orders:
    country = order.get("customer", {}).get("country", "UNKNOWN")
    orders_by_country[country].append(order["id"])
print(dict(orders_by_country))  # {'DE': [1, 3], 'FR': [2]}
```

---

### 85–90 | Homework Introduction

**Assignment:** Given a "dirty" orders JSON file (provided):
1. Parse with `json.load`.
2. Use `Counter` to find top-5 categories by order count.
3. Use `defaultdict` to compute total revenue per category.
4. Handle missing fields gracefully (`.get()` with defaults).
5. Output results as a clean JSON file.

**Evaluation criteria:** no manual `if key in dict` patterns, robust to missing fields, correct totals.

---

## Live Demo Script (comprehensive — spans whole lesson)

```python
# demo_lesson03.py
# "Dirty" orders data — missing fields, nested, repeated categories
import json
from collections import Counter, defaultdict
from pathlib import Path

orders = [
    {"id": 1, "category": "electronics", "amount": 500},
    {"id": 2, "category": "food"},                         # missing amount
    {"id": 3, "category": "electronics", "amount": 200},
    {"id": 4, "amount": 99},                               # missing category
    {"id": 5, "category": "food", "amount": 30},
    {"id": 6, "category": "food", "amount": 45},
]

# Step 1: Count with Counter
category_counts = Counter(
    o.get("category", "unknown") for o in orders
)
print("Order counts:", category_counts.most_common())

# Step 2: Revenue with defaultdict
revenue = defaultdict(float)
skipped = 0
for order in orders:
    cat = order.get("category", "unknown")
    amount = order.get("amount")
    if amount is None:
        skipped += 1
        continue
    revenue[cat] += amount

# Step 3: Build output
result = {
    "order_counts": dict(category_counts),
    "revenue_by_category": dict(revenue),
    "skipped_orders": skipped,
}

print(json.dumps(result, indent=2))
```

**Instructor narrates:** "Notice how `defaultdict` eliminates every `if category not in revenue` check. And `.get()` with a default makes missing fields a one-liner."

---

## Check for Understanding

**5-question quiz (minute 83):**

1. What is the time complexity of `x in my_set` vs `x in my_list` for large collections?
   > `my_set`: O(1). `my_list`: O(n). For 1M elements, the set is ~200× faster.

2. What does this print and why?
   ```python
   a = [1, 2]
   b = a
   b.append(3)
   print(a)
   ```
   > `[1, 2, 3]` — `b` is an alias for `a`, not a copy. They reference the same list object.

3. Rewrite this using `defaultdict`:
   ```python
   d = {}
   for k, v in data:
       if k not in d:
           d[k] = []
       d[k].append(v)
   ```
   > `from collections import defaultdict; d = defaultdict(list); [d[k].append(v) for k, v in data]`

4. Why can't you use a `list` as a dictionary key?
   > Lists are mutable and therefore not hashable. Dict keys must be hashable.

5. What is the output of `Counter("banana") - Counter("nan")`?
   > `Counter({'b': 1, 'a': 2})` — subtraction keeps only positive counts. `n: 2-2=0` and `a: 3-1=2`.

---

## Materials & Resources

- [collections module docs](https://docs.python.org/3/library/collections.html)
- [Python Data Model — hashability](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [copy module](https://docs.python.org/3/library/copy.html)
- Recommended reading: *Fluent Python* Ch. 2–3 (lists, dicts, sets)