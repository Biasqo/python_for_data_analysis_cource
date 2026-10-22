from multiprocessing import Pool
import time
import sys

def process_big_list(data):
    return sum(data)

def process_by_index(idx):
    chunk_size = 100_000 // 4  
    start = idx * chunk_size
    end = start + chunk_size
    data = list(range(start, end))
    return sum(data)

if __name__ == '__main__':
    # сериализация данных
    big_data = list(range(100_000_000))
    print(f"Размер: {sys.getsizeof(big_data) / 1024**2:.2f} MB")

    start = time.time()
    with Pool(4) as pool:
        results = pool.map(process_big_list, [big_data, big_data])
    print(f"{time.time() - start:.2f} сек")
    print(f"Результат: {results[0]}")

    # используем индекс для разбиения
    start = time.time()
    with Pool(4) as pool:
        results = pool.map(process_by_index, [0, 1, 2, 3])
    print(f"{time.time() - start:.2f} сек")
    print(f"Сумма всех частей: {sum(results)}")  # должно быть равно sum(range(100_000))