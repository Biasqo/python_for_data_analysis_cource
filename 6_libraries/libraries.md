# Lesson 6 — NumPy: Arrays and Vectorization
**Block 6 — Libraries | Duration: 90 minutes | Level: Intermediate/Advanced**

---

## Learning Objectives

By the end of this lesson, students will be able to:
1. Create and reshape NumPy arrays and understand how dtype affects memory and speed.
2. Use boolean indexing and broadcasting to select and transform data without loops.
3. Explain why vectorized code is faster than Python loops at a mechanistic level.
4. Apply `np.where`, axis-based aggregations, and basic linear algebra for economic data.

---

## Minute-by-Minute Plan

### 0–20 | Array Creation, dtypes, Shape

#### Why NumPy before pandas?
Pandas Series and DataFrame are built on NumPy arrays. Understanding NumPy prevents you from writing slow pandas code — `.apply(lambda x: ...)` over large DataFrames is essentially a Python loop in disguise.

#### Creating arrays
```python
import numpy as np

# From Python lists
a = np.array([1.0, 2.0, 3.0, 4.0])
print(a.dtype)   # float64
print(a.shape)   # (4,) — 1D, 4 elements

# 2D array (matrix)
m = np.array([[1, 2, 3], [4, 5, 6]])
print(m.shape)   # (2, 3) — 2 rows, 3 columns

# Factory functions
zeros   = np.zeros((3, 4), dtype=np.float32)
ones    = np.ones((2, 2))
eye     = np.eye(3)                   # identity matrix
arange  = np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)      # [0.0, 0.25, 0.5, 0.75, 1.0]
random  = np.random.randn(100, 5)    # 100 obs, 5 features, standard normal
```

#### dtypes — why they matter
```python
# Memory comparison
big_float64 = np.zeros(1_000_000, dtype=np.float64)
big_float32 = np.zeros(1_000_000, dtype=np.float32)
print(big_float64.nbytes)   # 8,000,000 bytes (8 MB)
print(big_float32.nbytes)   # 4,000,000 bytes (4 MB)

# Integer types
arr_int32 = np.array([1, 2, 3], dtype=np.int32)
arr_int64 = np.array([1, 2, 3], dtype=np.int64)

# Rule of thumb for economics data:
# float64 → prices, returns, GDP values (default, safest)
# float32 → ML feature matrices where memory matters
# int32   → counts, indices
# bool    → masks
```

#### Reshape
```python
flat = np.arange(12)             # [ 0  1  2 ... 11]
matrix = flat.reshape(3, 4)      # 3×4 matrix
column = flat.reshape(-1, 1)     # 12×1 column vector (-1 = infer)
row    = flat.reshape(1, -1)     # 1×12 row vector
```

---

### 20–45 | Indexing and Broadcasting

#### Slicing
```python
m = np.array([[10, 20, 30],
              [40, 50, 60],
              [70, 80, 90]])

print(m[0, :])      # [10 20 30]  — first row
print(m[:, 1])      # [20 50 80]  — second column
print(m[1:3, 0:2])  # [[40 50] [70 80]]  — submatrix
```

#### Boolean indexing
```python
prices = np.array([100.5, 85.0, 200.0, 50.0, 175.5])

# Create boolean mask
expensive = prices > 100
print(expensive)         # [True False True False True]

# Apply mask
print(prices[expensive]) # [100.5 200.0 175.5]

# Combined conditions
print(prices[(prices > 80) & (prices < 180)])  # [100.5 85.0 175.5]

# Where-based replacement
clipped = np.where(prices > 150, 150, prices)
print(clipped)  # [100.5  85.   150.    50.   150. ]
```

#### View vs Copy — critical for performance and correctness
```python
a = np.arange(10)

# Slices are VIEWS — share memory with original
b = a[2:5]
b[0] = 999
print(a)   # [  0   1 999   3   4   5   6   7   8   9]  ← original modified!

# Fancy indexing returns a COPY
c = a[[0, 3, 6]]
c[0] = -1
print(a)   # unchanged

# Force a copy
d = a[2:5].copy()
d[0] = 0
print(a)   # unchanged
```

#### Broadcasting — rules
```python
# Rule: dimensions are compatible if equal OR one of them is 1
# NumPy expands the dimension-1 axis to match the other

# Scalar broadcast
a = np.array([1, 2, 3])
print(a * 10)   # [10 20 30]

# 1D + 2D
row_vector = np.array([1, 2, 3])          # shape (3,)
matrix = np.ones((4, 3))                  # shape (4, 3)
result = matrix + row_vector              # shape (4, 3) — row added to each row
print(result)

# Column vector + row vector → 2D outer product
col = np.array([[1], [2], [3]])           # shape (3, 1)
row = np.array([10, 20, 30])             # shape (3,)
outer = col + row                         # shape (3, 3)
print(outer)
# [[11 21 31]
#  [12 22 32]
#  [13 23 33]]
```

---

### 45–70 | Vectorization

#### Why loops are slow — the interpreter overhead
```python
# Python loops: each iteration involves:
# 1. Type checking
# 2. Memory allocation for Python object
# 3. Bytecode dispatch
# NumPy: calls optimized C/Fortran routines on contiguous memory

# Demonstration with %timeit (run in Jupyter)
import numpy as np

N = 1_000_000
data = np.random.randn(N)

# Method 1: Python loop
def normalize_loop(arr):
    mean = sum(arr) / len(arr)
    std = (sum((x - mean)**2 for x in arr) / len(arr)) ** 0.5
    return [(x - mean) / std for x in arr]

# Method 2: List comprehension
def normalize_listcomp(arr):
    lst = arr.tolist()
    mean = sum(lst) / len(lst)
    std = (sum((x - mean)**2 for x in lst) / len(lst)) ** 0.5
    return [(x - mean) / std for x in lst]

# Method 3: NumPy vectorized (z-score normalization)
def normalize_numpy(arr):
    return (arr - arr.mean()) / arr.std()

# Typical results on 1M elements:
# loop         ~3000ms
# listcomp     ~300ms
# numpy        ~5ms  (600x faster than loop)
```

#### Vectorized operations reference
```python
arr = np.random.randn(1000)

# Aggregations
print(arr.mean(), arr.std(), arr.min(), arr.max())
print(arr.sum(), np.median(arr))

# Axis-based (2D)
m = np.random.randn(100, 5)
col_means = m.mean(axis=0)   # mean of each column (shape: 5,)
row_sums  = m.sum(axis=1)    # sum of each row (shape: 100,)

# Element-wise operations
returns = np.array([0.05, -0.02, 0.08, -0.01, 0.03])
cumulative = np.cumprod(1 + returns) - 1  # cumulative returns
print(cumulative)

# Boolean aggregations
print((arr > 0).sum())        # count of positive values
print((arr > 0).mean())       # proportion positive
```

#### `np.where` — vectorized if/else
```python
ratings = np.array([3.2, 4.8, 2.1, 4.1, 1.5, 3.9])

# Assign grade based on threshold
grades = np.where(ratings >= 4.0, "A",
         np.where(ratings >= 3.0, "B", "C"))
print(grades)  # ['B' 'A' 'C' 'A' 'C' 'B']
```

---

### 70–90 | Lab: Performance Benchmark

**Students run this in Jupyter and discuss results.**

```python
import numpy as np
import time

N = 1_000_000
data = np.random.randn(N)

def time_it(label, func, *args, reps=3):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        result = func(*args)
        times.append(time.perf_counter() - t0)
    avg = sum(times) / len(times)
    print(f"{label:30s}: {avg*1000:.1f}ms")
    return result

# --- Z-score normalization ---
def loop_normalize(arr):
    arr_list = arr.tolist()
    mean = sum(arr_list) / len(arr_list)
    std = (sum((x - mean) ** 2 for x in arr_list) / len(arr_list)) ** 0.5
    return [(x - mean) / std for x in arr_list]

def listcomp_normalize(arr):
    arr_list = arr.tolist()
    mean = sum(arr_list) / len(arr_list)
    std = (sum((x - mean) ** 2 for x in arr_list) / len(arr_list)) ** 0.5
    return [(x - mean) / std for x in arr_list]

def numpy_normalize(arr):
    return (arr - arr.mean()) / arr.std()

# Run benchmarks
time_it("Python loop", loop_normalize, data)
time_it("List comprehension", listcomp_normalize, data)
time_it("NumPy vectorized", numpy_normalize, data)

# Bonus: visualize speedup
import matplotlib.pyplot as plt
labels = ["Python loop", "List comp", "NumPy"]
# fill in actual timings from above
times_ms = [3000, 300, 5]   # approximate
plt.bar(labels, times_ms, color=["#d62728", "#ff7f0e", "#2ca02c"])
plt.ylabel("Time (ms)")
plt.title(f"Normalization of {N:,} elements")
plt.yscale("log")
plt.tight_layout()
plt.savefig("benchmark.png", dpi=150)
plt.show()
```

---

## Check for Understanding

**5 questions (minute 87):**

1. What is a NumPy "view" vs a "copy"? Give one case where confusing them causes a bug.
   > A view shares memory with the original array; modifying a view modifies the original. Bug example: `b = a[2:5]` then `b[0] = 0` silently changes `a`.

2. What shape does `np.ones((3, 1)) + np.ones((1, 4))` produce?
   > Shape `(3, 4)`. Broadcasting: the `(3,1)` expands columns to 4; the `(1,4)` expands rows to 3.

3. Why is `arr.mean()` faster than `sum(arr) / len(arr)`?
   > NumPy's `.mean()` calls a compiled C routine operating on contiguous memory without Python object overhead. `sum()` iterates in Python bytecode, boxing/unboxing each element.

4. What does `(prices > 100).sum()` compute?
   > The count of elements in `prices` that are greater than 100. Boolean arrays are treated as 0/1 integers when summed.

5. When would you use `float32` instead of the default `float64`?
   > When memory is constrained (e.g., large feature matrices for ML training) and the reduced precision (~7 decimal digits vs ~15) is acceptable. Typical use: neural network weights.