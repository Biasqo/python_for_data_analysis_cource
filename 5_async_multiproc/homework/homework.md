# Глава 5 - Домашнее задание: AsyncIO и Многопроцессорность

## Задание 1. Предскажите вывод

```python
import asyncio

async def task(name, delay):
    print(f"{name} начал")
    await asyncio.sleep(delay)
    print(f"{name} закончил")
    return delay

async def main():
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3),
    )
    print(results)

asyncio.run(main())
```

Опишите порядок печати строк и итоговое значение `results`.

## Задание 2. Найдите ошибку

Что произойдёт при выполнении этого кода? Объясните ошибку одним предложением.

```python
import asyncio

async def fetch_data():
    time.sleep(2)
    return "данные"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## Задание 3. `gather` или `TaskGroup`?

Чем поведение `asyncio.gather` отличается от `asyncio.TaskGroup` при возникновении исключения в одной из задач? Приведите пример ситуации, когда предпочтительнее `TaskGroup`.

## Задание 4. Предскажите вывод

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)
```

Будет ли результат всегда равен `400000`? Почему, учитывая наличие GIL?

## Задание 5. Заполните пропуски в таблице

| Конструкция | Что делает | Когда использовать |
|---|---|---|
| `asyncio.Semaphore(n)` | ??? | ??? |
| `multiprocessing.Pool` | ??? | ??? |
| `asyncio.to_thread(func)` | ??? | ??? |
| `shared_memory.SharedMemory` | ??? | ??? |

## Задание 6. Формула семафора - быстрый ответ

Дано: 10 задач (`N=10`), семафор с 2 разрешениями (`S=2`), каждая задача выполняется 3 секунды (`D=3`). Используя формулу `T = ceil(N / S) * D`, посчитайте общее время выполнения.

## Задание 7. `Pool` vs векторизация

Что выведет (концептуально) следующий фрагмент по производительности и почему это плохая практика?

```python
import pandas as pd
from multiprocessing import Pool

df = pd.DataFrame({"x": range(10_000_000)})

with Pool(4) as pool:
    results = pool.map(lambda chunk: chunk.sum(), [df, df, df, df])
```

## Задание 8. Asyncio vs Threading vs Multiprocessing

Перепишите обоснование выбора инструмента для следующей задачи и укажите, что вы выберете: нужно скачать содержимое 500 URL, а затем выполнить тяжёлую CPU-обработку (парсинг и агрегацию) каждого скачанного документа. Опишите двухэтапный подход с использованием подходящих инструментов из главы.

## Задание 9. `try`/`finally` в асинхронном коде - предскажите вывод

```python
import asyncio

async def worker():
    try:
        await asyncio.sleep(1)
        raise ValueError("ошибка в работе")
    finally:
        print("Ресурс освобождён")

async def main():
    try:
        await worker()
    except ValueError as e:
        print(f"Поймано: {e}")

asyncio.run(main())
```

## Задание 10. Асинхронный контекстный менеджер - базовый случай

В следующем классе пропущена реализация `__aexit__`. Допишите его так, чтобы соединение закрывалось **всегда**, даже если внутри блока `async with` возникло исключение, и чтобы исключение не подавлялось:

```python
class AsyncConnection:
    async def __aenter__(self):
        print("Подключение установлено")
        return self

    async def query(self, sql):
        print(f"Выполняется запрос: {sql}")

    # допишите __aexit__ здесь
```

Что произойдёт, если `__aexit__` вернёт `True` вместо `None`/`False`?