from multiprocessing import shared_memory
import numpy as np

if __name__ == '__main__':
    # Родительский процесс создаёт блок разделяемой памяти
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    shm_arr = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
    shm_arr[:] = arr[:]

    print("Имя блока разделяемой памяти:", shm.name)

    # "Дочерний" процесс подключается к тому же блоку по имени - без копирования
    existing_shm = shared_memory.SharedMemory(name=shm.name)
    view = np.ndarray(arr.shape, dtype=arr.dtype, buffer=existing_shm.buf)
    print("Данные, видимые из 'дочернего' подключения:", view)

    # Обязательная очистка
    existing_shm.close()
    shm.close()
    shm.unlink()