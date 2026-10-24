import os
from multiprocessing import Process, Queue


def worker(start: int, end: int, queue: Queue, worker_id: int) -> None:
    """Считает сумму квадратов и кладет результат в очередь"""
    result = sum(i**2 for i in range(start, end))
    queue.put(result)
    print(f"Worker {worker_id} (PID {os.getpid()})")


if __name__ == '__main__':
    cores = os.cpu_count()
    q = Queue()
    N = 100_000_000

    chunk = N // cores
    processes = []

    for i in range(cores):
        start = i * chunk
        end = start + chunk if i < cores - 1 else N  # последнему - остаток
        p = Process(target=worker, args=(start, end, q, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = 0
    while not q.empty():
        total += q.get()

    print(f"Сумма квадратов до {N}: {total}")
