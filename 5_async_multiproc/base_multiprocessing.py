from multiprocessing import Process, Queue

def worker(n: int) -> None:
    print(f"Сумма квадратов до {n}: {sum(i**2 for i in range(n))}")

if __name__ == '__main__':
    N = 100_000_000
    p = Process(target=worker, args=(N,))
    p.start()
    p.join()
    print("Дочерний процесс завершён")