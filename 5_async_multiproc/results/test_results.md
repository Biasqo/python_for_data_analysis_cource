# Глава 5 - тест ответы

## Решение 1. Заблокированный event loop

**1. Почему код не работает как задумано.**
`fetch_data` — обычная синхронная функция, а не корутина. `asyncio.gather(*tasks)` ожидает на входе awaitable-объекты (корутины, задачи, футуры). Здесь список `tasks` на самом деле уже содержит **результаты** вызовов `fetch_data(i)` (то есть `int`, а не awaitable), потому что `fetch_data(i)` вызывается синхронно ещё до передачи в `gather`. Код либо упадёт с `TypeError`, либо (если бы `fetch_data` была корутиной, но без `await asyncio.sleep`) всё равно заблокировал бы event loop через `time.sleep`, выполняясь строго последовательно.

**2. Исправленная версия:**
```python
import asyncio

async def fetch_data(n):
    await asyncio.sleep(1)  # неблокирующая имитация I/O
    return n * 2

async def main():
    tasks = [fetch_data(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```
Теперь все 10 корутин запланированы одновременно, `await asyncio.sleep(1)` освобождает управление event loop'у, и весь `main()` займёт ~1 секунду вместо ~10.

**3. Обёртка над legacy-синхронной функцией:**
```python
import asyncio
import time

def legacy_fetch_data(n):
    time.sleep(1)
    return n * 2

async def main():
    loop = asyncio.get_running_loop()
    tasks = [asyncio.to_thread(legacy_fetch_data, i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```
`asyncio.to_thread` выполняет блокирующую функцию в отдельном потоке пула, не блокируя event loop, что позволяет получить конкурентность даже для кода, который нельзя переписать на `async def`.

---

## Решение 2. Rate-limited краулер с Semaphore

```python
import asyncio
import random
import time

async def fetch_one(url, semaphore, results, index):
    async with semaphore:
        start = time.monotonic()
        print(f"[{start:.2f}] START {url}")
        await asyncio.sleep(random.uniform(0.2, 1.0))  # имитация запроса
        status = 200
        print(f"[{time.monotonic():.2f}] DONE  {url}")
        results[index] = status

async def fetch_all(urls, max_concurrent):
    semaphore = asyncio.Semaphore(max_concurrent)
    results = [None] * len(urls)
    tasks = [
        fetch_one(url, semaphore, results, i)
        for i, url in enumerate(urls)
    ]
    await asyncio.gather(*tasks)
    return results

async def main():
    urls = [f"http://example.com/{i}" for i in range(20)]
    start = time.monotonic()
    results = await fetch_all(urls, max_concurrent=5)
    elapsed = time.monotonic() - start
    print(results)
    print(f"Elapsed: {elapsed:.2f}s")

asyncio.run(main())
```

Список `results` заполняется по индексу, а не через `append`, поэтому порядок результатов гарантированно совпадает с порядком входных `urls`, даже если запросы завершаются в разное время.

По формуле `T = ceil(N / S) * D`: при `N = 20`, `S = 5` и среднем `D ≈ 0.6` сек (середина диапазона `0.2–1.0`) ожидаемое время — `ceil(20/5) * 0.6 = 4 * 0.6 = 2.4` сек. Фактическое время будет близко к этому значению, но не идентично, так как реальная длительность каждого запроса случайна, а не фиксирована — формула из лекции даёт лишь оценку при равных `D`.

---

## Решение 3. TaskGroup и отмена при ошибке

**1.** В коде на `asyncio.gather` (без `return_exceptions=True`) при возникновении исключения в `worker(2)` сам `gather` немедленно поднимет это исключение в `main()`, но `worker(3)` и `worker(4)` **не будут отменены** — они продолжат выполняться в фоне как обычные задачи event loop, просто их результаты уже никто не заберёт. Это именно та проблема "потерянных" задач, о которой говорится в главе про структурную конкурентность.

**2.** Исправленная версия с `TaskGroup`:
```python
import asyncio

async def worker(i):
    await asyncio.sleep(i)
    if i == 2:
        raise ValueError(f"worker {i} failed")
    return i

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(worker(1))
            tg.create_task(worker(2))
            tg.create_task(worker(3))
            tg.create_task(worker(4))
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"Caught: {exc}")

asyncio.run(main())
```
`TaskGroup` при выходе из блока `async with` с исключением автоматически отменяет все ещё не завершённые дочерние задачи и поднимает `ExceptionGroup`, которую нужно ловить через `except*`.

**3.** Демонстрация реальной отмены `worker(4)`:
```python
import asyncio, time

async def worker(i):
    try:
        await asyncio.sleep(i)
        if i == 2:
            raise ValueError(f"worker {i} failed")
        return i
    except asyncio.CancelledError:
        print(f"[{time.monotonic():.2f}] worker {i} CANCELLED")
        raise

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            for i in (1, 2, 3, 4):
                tg.create_task(worker(i))
    except* ValueError:
        pass

asyncio.run(main())
```
Так как `worker(2)` падает на 2-й секунде, а `worker(4)` должен был бы завершиться только на 4-й, вывод покажет строку `worker 4 CANCELLED` примерно на 2-й секунде — то есть задача реально прервана, а не просто проигнорирована после завершения `main()`.

---

## Решение 4. Сравнение threading, asyncio и multiprocessing на CPU-bound задаче

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_bound(n):
    return sum(i * i for i in range(n))

N = 20_000_000
CALLS = 4

def run_sequential():
    start = time.perf_counter()
    for _ in range(CALLS):
        cpu_bound(N)
    return time.perf_counter() - start

def run_threads():
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(cpu_bound, [N] * CALLS))
    return time.perf_counter() - start

def run_processes():
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as ex:
        list(ex.map(cpu_bound, [N] * CALLS))
    return time.perf_counter() - start

if __name__ == "__main__":
    print("Sequential:", run_sequential())
    print("Threading: ", run_threads())
    print("Processes: ", run_processes())
```

Примерная (иллюстративная) таблица результатов — точные цифры зависят от машины:

| Способ | Время (сек, ориентировочно) |
|---|---|
| Последовательно | ~4.0 |
| ThreadPoolExecutor | ~4.1–4.3 (часто немного медленнее!) |
| ProcessPoolExecutor | ~1.2–1.5 |

Ускорения от threading не ожидается, потому что GIL сериализует исполнение байткода — потоки лишь чередуются на одном ядре, а не выполняются одновременно. Threading-версия часто оказывается даже *медленнее* последовательной из-за накладных расходов на переключение контекста между потоками (context switching), которые в данном случае ничем не компенсируются, так как выигрывает только I/O-часть, а её здесь нет. `ProcessPoolExecutor` даёт реальное ускорение, поскольку у каждого процесса свой собственный интерпретатор и свой GIL, и вычисления действительно выполняются параллельно на разных ядрах.

---

## Решение 5. Гонка данных в multiprocessing

**1. Природа гонки.** `Value("i", 0)` создаёт объект в **разделяемой** памяти (в отличие от обычных объектов Python при multiprocessing, которые копируются в каждый процесс независимо). Операция `counter.value += 1` не атомарна — это фактически три шага: прочитать значение, увеличить его, записать обратно. Когда 4 процесса выполняют эти шаги одновременно без синхронизации, некоторые инкременты «теряются»: один процесс читает старое значение до того, как другой успел записать своё увеличенное значение, поэтому итоговая сумма получается меньше 400 000.

**2. Исправленная версия с `Lock`:**
```python
from multiprocessing import Process, Value, Lock

def worker(counter, lock, n):
    for _ in range(n):
        with lock:
            counter.value += 1

if __name__ == "__main__":
    counter = Value("i", 0)
    lock = Lock()
    processes = [Process(target=worker, args=(counter, lock, 100_000)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print(counter.value)  # теперь всегда 400000
```

**3. Замедление.** Добавление `Lock` заметно замедляет выполнение (часто в несколько раз), потому что каждый инкремент теперь требует захвата и освобождения межпроцессной блокировки — это системный вызов с существенными накладными расходами, и при 400 000 итераций конкуренция за блокировку становится узким местом, фактически сериализуя всю работу между процессами, сводя параллелизм на этом конкретном участке почти к нулю.

---

## Решение 6. pickle vs shared_memory

**1–3. Версия с `shared_memory`:**
```python
import numpy as np
from multiprocessing import Pool
from multiprocessing.shared_memory import SharedMemory

def process_chunk(args):
    shm_name, shape, dtype, start, end = args
    shm = SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
    result = arr[start:end].sum()
    shm.close()
    return result

if __name__ == "__main__":
    size = 100_000_000
    source = np.random.rand(size)

    shm = SharedMemory(create=True, size=source.nbytes)
    shared_arr = np.ndarray(source.shape, dtype=source.dtype, buffer=shm.buf)
    shared_arr[:] = source[:]

    chunk_size = size // 4
    tasks = [
        (shm.name, source.shape, source.dtype, i * chunk_size, (i + 1) * chunk_size)
        for i in range(4)
    ]

    with Pool(4) as pool:
        results = pool.map(process_chunk, tasks)

    print(sum(results))

    shm.close()
    shm.unlink()
```

Разница по времени: «плохая» версия с pickle-копированием тратит существенную долю времени именно на сериализацию и передачу ~800 МБ (100 млн `float64`) в каждый из 4 процессов, то есть фактически до 3.2 ГБ трафика IPC. Версия с `shared_memory` копирует массив в общую память только **один раз** при создании, а дочерние процессы получают доступ к данным напрямую через `numpy.ndarray` без копирования, поэтому суммарное время выполнения обычно заметно меньше, особенно с ростом размера массива. Важно вызывать `shm.close()` в каждом процессе (включая дочерние) и `shm.unlink()` один раз в родительском процессе после завершения работы, иначе блок памяти останется висеть в системе.

---

## Решение 7. Асинхронный генератор с пагинацией

```python
import asyncio
import random

async def fetch_page(page_number, total_pages):
    await asyncio.sleep(0.3)
    if total_pages > 7 and page_number == 7:
        return []  # пустая страница — сигнал остановки
    if page_number >= total_pages:
        return []
    return [random.randint(1, 100) for _ in range(10)]

async def paginated_fetch(total_pages):
    page_number = 0
    while True:
        page = await fetch_page(page_number, total_pages)
        if not page:
            break
        yield page
        page_number += 1

async def collect_all(total_pages):
    all_items = []
    async for page in paginated_fetch(total_pages):
        all_items.extend(page)
    return all_items
```

Версия с `Queue` для параллельной обработки:
```python
async def producer(queue, total_pages):
    async for page in paginated_fetch(total_pages):
        await queue.put(page)
    await queue.put(None)  # сигнал завершения

async def consumer(queue, processed):
    while True:
        page = await queue.get()
        if page is None:
            break
        # имитация обработки страницы
        await asyncio.sleep(0.1)
        processed.extend(x * 2 for x in page)

async def main():
    queue = asyncio.Queue()
    processed = []
    await asyncio.gather(
        producer(queue, total_pages=10),
        consumer(queue, processed),
    )
    print(processed)

asyncio.run(main())
```
Producer получает следующую страницу, пока consumer обрабатывает предыдущую — эти операции идут конкурентно, а не строго последовательно.

---

## Решение 8. Диагностика проблем в коде

**Три проблемы:**
1. `fetch(None, url)` — передаётся `None` вместо реального `aiohttp.ClientSession`; сессию нужно создавать один раз и переиспользовать для всех запросов, а не создавать/пропускать её на каждый вызов.
2. `Pool(4)` создаётся заново на каждой итерации цикла внутри `async def main` — создание пула процессов дорогая операция (запуск новых интерпретаторов), к тому же синхронный `.map()` внутри корутины **блокирует event loop** на время ожидания результата от процессов.
3. Цикл `for url in urls: html = await fetch(...)` выполняет запросы строго последовательно, а не конкурентно — конкурентность здесь фактически не используется, несмотря на `asyncio`.

**Исправленная версия:**
```python
import asyncio
import aiohttp
from concurrent.futures import ProcessPoolExecutor

def parse(html):
    return len(html)

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def fetch_and_parse(session, url, executor, loop):
    html = await fetch(session, url)
    parsed = await loop.run_in_executor(executor, parse, html)
    return parsed

async def main(urls):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_and_parse(session, url, executor, loop) for url in urls]
            results = await asyncio.gather(*tasks)
    return results

asyncio.run(main(["http://a.com", "http://b.com"]))
```
Сессия и пул процессов создаются один раз вне цикла, все запросы запускаются конкурентно через `gather`, а CPU-тяжёлая `parse` выполняется в отдельных процессах, не блокируя event loop.

---

## Решение 9. Проектирование системы сбора логов

Архитектура (по уровням):

```
[100 источников]  --- I/O, ограничение 20 одновременных ---
        │
        ▼
  asyncio.Semaphore(20) + TaskGroup
  (каждая задача — один источник; ошибка в одном источнике
   не должна ронять остальные -> try/except внутри задачи,
   а не полагаться на автоотмену TaskGroup)
        │
        ▼
  asyncio.Queue  (сырые строки логов, producer'ы кладут в очередь)
        │
        ▼
  ProcessPoolExecutor  (CPU-bound: regex-парсинг + хэширование,
   вызывается через loop.run_in_executor из consumer-корутины)
        │
        ▼
  Буфер батчей по 500 записей (обычный список/deque)
        │
        ▼
  asyncio.to_thread(write_batch_to_disk) или aiofiles
  (I/O-bound запись на диск, не блокирует event loop)
```

Ключевые решения:
- Ограничение в 20 соединений — через `asyncio.Semaphore(20)`, оборачивающий подключение к каждому источнику.
- Изоляция ошибок отдельного источника — **не** используем `TaskGroup` для верхнего уровня (он отменил бы все остальные источники при одной ошибке), а оборачиваем каждую задачу-источник в собственный `try/except`, логируем ошибку и продолжаем работу с остальными 99 источниками.
- CPU-тяжёлый парсинг и хэширование выносится в `ProcessPoolExecutor`, чтобы не блокировать event loop и использовать несколько ядер.
- Батчинг по 500 записей и запись через `asyncio.to_thread` (или `aiofiles`) — I/O-bound, не должно блокировать приём новых логов.

Скелет кода:
```python
import asyncio

SEM = asyncio.Semaphore(20)
BATCH_SIZE = 500

async def read_source(source_id, queue):
    async with SEM:
        try:
            # TODO: тут был бы реальный сокет / подключение к источнику
            while True:
                line = await fake_read_line(source_id)
                if line is None:
                    break
                await queue.put(line)
        except Exception as e:
            print(f"source {source_id} failed: {e}")

async def fake_read_line(source_id):
    await asyncio.sleep(0.05)
    return f"log from {source_id}"

async def consumer(queue, executor, loop):
    batch = []
    while True:
        line = await queue.get()
        processed = await loop.run_in_executor(executor, heavy_parse, line)
        batch.append(processed)
        if len(batch) >= BATCH_SIZE:
            await asyncio.to_thread(write_batch, batch)
            batch = []

def heavy_parse(line):
    # TODO: regex-парсинг + хэширование
    return line

def write_batch(batch):
    # TODO: запись в файл
    pass

async def main():
    from concurrent.futures import ProcessPoolExecutor
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()
    with ProcessPoolExecutor(max_workers=4) as executor:
        sources = [read_source(i, queue) for i in range(100)]
        await asyncio.gather(consumer(queue, executor, loop), *sources)

asyncio.run(main())
```

---

## Решение 10. Профилирование степени параллелизма

```python
import time
import os
from concurrent.futures import ProcessPoolExecutor

def heavy_computation(x):
    time.sleep(0.5)  # ВНИМАНИЕ: это имитация I/O, а не CPU-bound нагрузки;
    return x           # для настоящей CPU-bound задачи выводы по масштабированию
                        # были бы ограничены количеством физических ядер,
                        # а не показывали бы линейный рост до 32 воркеров

def benchmark(n_tasks, n_workers):
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        list(ex.map(heavy_computation, range(n_tasks)))
    return time.perf_counter() - start

if __name__ == "__main__":
    print("CPU count:", os.cpu_count())
    for n_workers in [1, 2, 4, 8, 16, 32]:
        t = benchmark(32, n_workers)
        print(f"n_workers={n_workers:2d}  time={t:.2f}s")
```

Ожидаемая форма результата (иллюстративно, для `n_tasks = 32` и `time.sleep(0.5)` в качестве заглушки под I/O):

| n_workers | Время, сек (ориентировочно) |
|---|---|
| 1 | ~16.0 |
| 2 | ~8.0 |
| 4 | ~4.0 |
| 8 | ~2.0 |
| 16 | ~1.0 |
| 32 | ~0.5 |

Поскольку в этой версии `heavy_computation` имитирует I/O через `time.sleep`, время продолжает почти линейно уменьшаться даже при `n_workers > os.cpu_count()`, так как процессы большую часть времени просто «спят» и не конкурируют за CPU. **Если бы `heavy_computation` была настоящей CPU-bound функцией** (например, тяжёлый математический цикл), выигрыш перестал бы расти уже примерно при `n_workers ≈ os.cpu_count()` — дальнейшее увеличение числа процессов не даёт ускорения, а лишь добавляет накладные расходы на создание процессов и переключение контекста между ними, потому что физических ядер для параллельного исполнения больше не хватает.