from multiprocessing import Pool
import time

N = 150_000_000
CHUNKS = 4


def cpu_bound(n: int) -> int:
    return sum(i * i for i in range(n))


if __name__ == '__main__':
    start = time.time()
    for _ in range(CHUNKS):
        cpu_bound(N // CHUNKS)
    sequential_time = time.time() - start

    start = time.time()
    with Pool(processes=CHUNKS) as pool:
        pool.map(cpu_bound, [N // CHUNKS] * CHUNKS)
    multiprocessing_time = time.time() - start

    print(f"Multiprocessing : {multiprocessing_time:.2f} сек.\n")
    print(f"Sequental : {sequential_time:.2f} сек  sequential\n")
