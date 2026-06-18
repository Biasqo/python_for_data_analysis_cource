# Lesson 5 — AsyncIO and Multiprocessing
**Block 5 — Async & Parallelism | Duration: 90 minutes | Level: Intermediate/Advanced**

---

## Learning Objectives

By the end of this lesson, students will be able to:
1. Explain the GIL and its practical implications for CPU-bound vs I/O-bound tasks.
2. Write `async/await` code using `asyncio.gather` for concurrent I/O.
3. Parallelize CPU-bound work with `multiprocessing.Pool`.
4. Select the right concurrency tool for a given data analysis task.

---

## Minute-by-Minute Plan

### 0–15 | Concurrency vs Parallelism, and the GIL

**Key concepts — define carefully:**

| Term | Definition |
|---|---|
| **Concurrency** | Handling multiple tasks by interleaving progress (single core) |
| **Parallelism** | Actually running multiple tasks simultaneously (multiple cores) |
| **GIL** | Global Interpreter Lock — only one thread executes Python bytecode at a time |

```
                CPU-bound task         I/O-bound task
                (computation)          (network/disk)
Threading       ❌ GIL blocks           ✅ Threads release GIL during I/O
Asyncio         ❌ Single-threaded      ✅ Cooperative multitasking
Multiprocessing ✅ Bypasses GIL        ⚠️  Overhead from serialization
```

**Analogy:** Think of the GIL as a single toll booth on a highway. Even if you have multiple cars (threads), only one gets through at a time. For long I/O waits, the car steps aside and lets others through. But for pure computation (driving fast), you need multiple parallel highways (processes).

**Why does this matter for economists/data analysts?**
- Batch API calls (fetch macro data) → asyncio.
- Parallel preprocessing of large CSV files → multiprocessing.
- Pandas `.apply()` on large DataFrames → multiprocessing (or vectorize!).

---

### 15–45 | AsyncIO

#### Core concepts
```python
import asyncio

# A coroutine — defined with async def
async def greet(name: str, delay: float) -> str:
    await asyncio.sleep(delay)   # non-blocking wait (releases event loop)
    return f"Hello, {name}!"

# Running a single coroutine
result = asyncio.run(greet("Alice", 1.0))
print(result)  # Hello, Alice!
```

#### `asyncio.gather` — concurrent execution
```python
import asyncio
import time

async def fetch_country_gdp(country: str) -> dict:
    """Simulate API call to a macro database."""
    delays = {"DE": 0.5, "FR": 0.8, "IT": 1.2}
    await asyncio.sleep(delays.get(country, 1.0))
    gdp_data = {"DE": 4.07, "FR": 2.78, "IT": 2.10}
    return {"country": country, "gdp_tn_usd": gdp_data[country]}

async def main():
    countries = ["DE", "FR", "IT"]
    start = time.perf_counter()

    # Sequential — total time = 0.5 + 0.8 + 1.2 = 2.5s
    # results = [await fetch_country_gdp(c) for c in countries]

    # Concurrent with gather — total time ≈ max(0.5, 0.8, 1.2) = 1.2s
    results = await asyncio.gather(*[fetch_country_gdp(c) for c in countries])

    elapsed = time.perf_counter() - start
    print(f"Fetched {len(results)} countries in {elapsed:.2f}s")
    print(results)

asyncio.run(main())
```

#### Async context managers — for resources that need teardown
```python
import asyncio
import aiohttp  # pip install aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# urls = ["https://api.worldbank.org/v2/country/DE/indicator/NY.GDP.MKTP.CD?format=json", ...]
# results = asyncio.run(fetch_all(urls))
```

#### Error handling in gather
```python
async def risky_fetch(i: int):
    await asyncio.sleep(0.1)
    if i == 2:
        raise ValueError(f"Task {i} failed")
    return i * 10

async def main():
    # return_exceptions=True — failures don't cancel other tasks
    results = await asyncio.gather(
        *[risky_fetch(i) for i in range(5)],
        return_exceptions=True
    )
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"Task {i} error: {r}")
        else:
            print(f"Task {i} result: {r}")

asyncio.run(main())
```

---

### 45–70 | Multiprocessing

#### Basic `Process`
```python
from multiprocessing import Process

def worker(n: int) -> None:
    result = sum(i**2 for i in range(n))
    print(f"Sum of squares to {n}: {result}")

if __name__ == "__main__":  # CRITICAL — required on Windows/macOS
    p = Process(target=worker, args=(1_000_000,))
    p.start()
    p.join()   # wait for completion
```

**Why `if __name__ == "__main__"`?**
On Windows, new processes import the module — without this guard, you get infinite recursion as each child spawns more children.

#### `Pool.map` — parallelize over a list
```python
from multiprocessing import Pool
import time

def compute_stats(filepath: str) -> dict:
    """CPU-bound: read file + compute statistics."""
    import csv
    with open(filepath) as f:
        amounts = [float(row["amount"]) for row in csv.DictReader(f)]
    return {
        "file": filepath,
        "total": sum(amounts),
        "count": len(amounts),
        "avg": sum(amounts) / len(amounts),
    }

if __name__ == "__main__":
    files = [f"data/batch_{i:03d}.csv" for i in range(20)]

    # Sequential
    t0 = time.perf_counter()
    sequential = [compute_stats(f) for f in files]
    print(f"Sequential: {time.perf_counter() - t0:.2f}s")

    # Parallel (uses all CPU cores)
    t0 = time.perf_counter()
    with Pool() as pool:
        parallel = pool.map(compute_stats, files)
    print(f"Parallel ({Pool()._processes} cores): {time.perf_counter() - t0:.2f}s")
```

#### `imap` — lazy iteration for large inputs
```python
from multiprocessing import Pool

def process_row(row: dict) -> float:
    return float(row["amount"]) * 1.2  # some transformation

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        # imap is lazy — doesn't load all results into memory at once
        for result in pool.imap(process_row, large_row_list, chunksize=500):
            # process each result as it comes
            pass
```

#### Serialization overhead — when multiprocessing isn't worth it
```python
# Passing data between processes requires pickle serialization
# Small data: overhead > speedup
# Rule of thumb: if each task < 100ms, consider vectorization instead

import pickle
import time

big_array = list(range(1_000_000))

t0 = time.perf_counter()
serialized = pickle.dumps(big_array)
deserialized = pickle.loads(serialized)
print(f"Pickle round-trip: {time.perf_counter() - t0:.3f}s")
# If your task takes less than this, multiprocessing won't help
```

---

### 70–85 | Decision Tree

**Post this on screen and work through it with the class:**

```
Is the task I/O-bound? (network, disk, API calls)
├── Yes → asyncio (or threading for blocking libs)
└── No → Is it CPU-bound? (computation, parsing, ML)
           ├── Yes → multiprocessing.Pool
           │         ├── But: is data huge to serialize? → consider vectorization (NumPy)
           │         └── Or: does each task < 100ms? → not worth the overhead
           └── No → just sequential code is fine
```

**Concrete data analysis mappings:**

| Task | Right tool | Why |
|---|---|---|
| Download 100 CSVs from S3 | asyncio / aiohttp | I/O-bound |
| Batch API calls to Bloomberg | asyncio | I/O-bound |
| Parallel preprocessing of 50 CSV files | multiprocessing.Pool | CPU-bound |
| Train ML models with different hyperparams | multiprocessing.Pool | CPU-bound |
| Normalize a 10M-row DataFrame | NumPy vectorization | Avoid overhead entirely |
| Real-time event streaming | asyncio | Concurrent I/O |

---

### 85–90 | Homework Introduction

**Assignment:**
1. Write an `async` function that fetches economic indicators for 20 countries from a mock API (provided as local server).
2. Use `asyncio.gather` with `return_exceptions=True` and report which countries failed.
3. For the parsing/aggregation step, use `multiprocessing.Pool.map` and compare timing to sequential.

---

## Live Demo: Three Versions of the Same Task

```python
# Task: "Download 50 files and count lines in each"
# Simulated with sleep(0.1) for download and computation

import asyncio
import time
from multiprocessing import Pool

# --- Version 1: Synchronous ---
def download_sync(i):
    time.sleep(0.1)   # I/O simulation
    return sum(range(10_000))  # CPU simulation

def run_sync(n=10):
    t0 = time.perf_counter()
    results = [download_sync(i) for i in range(n)]
    print(f"Sync: {time.perf_counter() - t0:.2f}s")

# --- Version 2: AsyncIO (I/O-bound wins) ---
async def download_async(i):
    await asyncio.sleep(0.1)   # non-blocking I/O simulation
    return i * 100

async def run_async(n=10):
    t0 = time.perf_counter()
    results = await asyncio.gather(*[download_async(i) for i in range(n)])
    print(f"Async: {time.perf_counter() - t0:.2f}s")

# --- Version 3: Multiprocessing (CPU-bound wins) ---
def cpu_task(i):
    return sum(range(1_000_000))  # pure CPU

def run_multiprocessing(n=10):
    t0 = time.perf_counter()
    with Pool() as pool:
        results = pool.map(cpu_task, range(n))
    print(f"Multiprocessing: {time.perf_counter() - t0:.2f}s")

if __name__ == "__main__":
    run_sync(10)
    asyncio.run(run_async(10))
    run_multiprocessing(10)
```

---

## Check for Understanding

**5 questions (minute 83):**

1. Why does the GIL prevent threads from speeding up CPU-bound tasks?
   > The GIL ensures only one thread executes Python bytecode at a time. Multiple threads can't run Python code in parallel — they take turns. For pure computation, this yields no speedup.

2. What does `await asyncio.sleep(1)` do differently from `time.sleep(1)`?
   > `asyncio.sleep` suspends the coroutine and releases the event loop to run other coroutines. `time.sleep` blocks the entire thread, preventing any concurrent execution.

3. Why must multiprocessing code be inside `if __name__ == "__main__"`?
   > On Windows/macOS, new processes are created by importing the module. Without the guard, each child process would spawn more children, causing infinite recursion.

4. You need to call a REST API 200 times. Which tool and why?
   > `asyncio` with `aiohttp` — this is I/O-bound. Async handles many concurrent requests efficiently without the overhead of multiple processes.

5. `Pool.map` serializes arguments with pickle. When does this overhead make multiprocessing not worth it?
   > When each individual task completes in less time than the serialization round-trip (~milliseconds for large data). Small, fast tasks often run faster sequentially.