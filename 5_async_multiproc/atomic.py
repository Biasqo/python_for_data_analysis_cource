from multiprocessing import Process, Value, Lock

# N = 1000
# N = 10000
N = 200_000
# N = 1_000_000


def increment_lock(counter, lock):
    for _ in range(N):
        with lock:
            counter.value += 1


def increment(counter):
    for _ in range(N):
        counter.value += 1


if __name__ == '__main__':
    counter = Value('i', 0)
    p1 = Process(target=increment, args=(counter,))
    p2 = Process(target=increment, args=(counter,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"Без блокировки: {counter.value}")

    lock = Lock()
    counter = Value('i', 0)
    p1 = Process(target=increment_lock, args=(counter, lock))
    p2 = Process(target=increment_lock, args=(counter, lock))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"С блокировкой: {counter.value}")
