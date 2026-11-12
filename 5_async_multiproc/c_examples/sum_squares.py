import ctypes
import numpy as np
from multiprocessing import Pool
import time

lib = ctypes.CDLL('./sum_squares.so')

lib.sum_of_squares_parallel.argtypes = [
    ctypes.POINTER(ctypes.c_int), ctypes.c_long]
lib.sum_of_squares_parallel.restype = ctypes.c_longlong


def cpu_bound(chunk):
    return int(np.sum(chunk.astype(np.int64) ** 2))


if __name__ == '__main__':
    n = 1000000000
    chunks = 8
    arr = np.arange(n, dtype=np.int32) % 1000

    start = time.time()
    result = lib.sum_of_squares_parallel(
        arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        ctypes.c_long(n),
    )
    c_time = time.time() - start

    print("Sum of squares =", result)
    print(f"c_time : {c_time:.2f} сек.\n")

    parts = np.array_split(arr, chunks)

    start = time.time()
    with Pool(processes=chunks) as pool:
        results = pool.map(cpu_bound, parts)
    mp_time = time.time() - start

    mp_result = sum(results)

    print(f"threads actually used = {chunks}")
    print("Sum of squares =", mp_result)
    print(f"Multiprocessing : {mp_time:.2f} сек.\n")
