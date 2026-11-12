# Домашнее задание 3.

```text
Каждое задание оценивается в **4 балла**
```

#### 1. Асинхронный загрузчик страниц

**Описание**
Нужно скачать 20 страниц. \
Часть запросов падает с ошибкой, а сервер разрешает не более 5 одновременных соединений. \
Сеть имитируется через `asyncio.sleep`. Функцию `fetch` менять нельзя. 

```python
import asyncio
import random
import time

random.seed(7)
URLS = [f"https://example.com/page/{i}" for i in range(1, 21)]

class FetchError(Exception):
    pass

async def fetch(url: str) -> str:
    await asyncio.sleep(random.uniform(0.3, 1.0))
    if random.random() < 0.25:
        raise FetchError(f"Ошибка при загрузке {url}")
    return f"<html>{url}</html>"
```

**Задание**
* Напишите `fetch_with_retry(url, retries=3, delay=0.2)`: при `FetchError` ждёт `delay` секунд и повторяет попытку, после последней неудачной попытки пробрасывает исключение.
* Напишите `download_all(urls, limit=5)`: загружает страницы конкурентно, не более `limit` одновременно, результаты возвращает в порядке `urls`.
* Добавьте счётчик активных запросов и выведите его значение в пике.
* Сравните время при `limit=1`, `5`, `20` и при последовательной загрузке.

**Примеры** (числа у вас будут другие)
```text
Загружено: 18, упало: 2
Пик одновременных запросов: 5
Время: 4.5 с (последовательно: ~20 с)
```

**Подсказка**
Используйте семафор для ограничения запросов. Использовать `time.sleep` внутри coroutine нельзя.

#### 2. TaskGroup, async for, async with

Данные читаются постранично через connection, каждая страница обрабатывается *отдельной* задачей. \
Если обработка любой страницы падает, остальные задачи отменяются, а соединение должно быть закрыто.

```python
import asyncio

TOTAL_PAGES = 10
PAGE_SIZE = 5

def make_record(record_id: int, poison_id: int | None) -> dict:
    if record_id == poison_id:
        value = -1
    else:
        value = record_id % 17 + 1
    return {"id": record_id, "value": value}
```

**Задание**
* `connection()` - асинхронный контекстный менеджер: при входе печатает `open` (ждёт 0.1 с), при выходе ждёт 0.1 с и печатает `close`, в том числе при исключении внутри блока.
* `read_pages(conn, poison_id=None)` - асинхронный генератор: 10 раз ждёт 0.2 с и отдаёт страницу из 5 записей (через `make_record`, `id` сквозные: 0, 1, 2, ...).
* `process_page(page)` - ждёт 0.1 с и возвращает сумму `value` по странице, при `value < 0` бросает `ValueError`.
* `run(poison_id)` - открывает `connection`, внутри `TaskGroup` читает страницы через `async for` и создаёт задачи, ошибки ловит через `except*`.
* Запустите `run(None)` и `run(42)`.
* В `markdown` ячейке или комментарии ответьте: чем `TaskGroup` отличается от `asyncio.gather` при ошибке в одной из задач?

**Примеры**
```text
run(None):
open
close
total 442

run(42):
open
close
caught: ValueError('negative')
```

**Подсказка**
Контекстный менеджер можно написать через `@asynccontextmanager` из `contextlib`. При ошибке `TaskGroup` отменяет все дочерние задачи и собирает исключения в `ExceptionGroup`.

#### 3. Работа с данными

**Описание**
Нужно построить отчёт «топ-3 категории по выручке в каждом регионе» двумя способами и сравнить их.

Подготовка данных (установите `pandas`, `polars`, `numpy`, `pyarrow`):
```python
from pathlib import Path
import numpy as np
import pandas as pd

N = 3_000_000
rng = np.random.default_rng(42)
Path("data").mkdir(exist_ok=True)

orders = pd.DataFrame({
    "order_id":    np.arange(N),
    "customer_id": rng.integers(1, 50_001, N),
    "category":    rng.choice(["еда", "электроника", "одежда", "книги", "транспорт"], N),
    "amount":      rng.gamma(2.0, 400.0, N).round(2),
    "order_dt":    pd.Timestamp("2024-01-01")
                   + pd.to_timedelta(rng.integers(0, 366 * 24 * 3600, N), unit="s"),
})
orders.loc[rng.random(N) < 0.02, "amount"] = np.nan

customers = pd.DataFrame({
    "customer_id": np.arange(1, 50_001),
    "region":  rng.choice(["Москва", "Урал", "Сибирь", "Юг", "Поволжье"], 50_000),
    "segment": rng.choice(["B2C", "B2B"], 50_000, p=[0.8, 0.2]),
})

orders.to_parquet("data/orders.parquet", index=False)
customers.to_parquet("data/customers.parquet", index=False)
```

**Задание**
Реализуйте один и тот же пайплайн на **pandas** и на **Polars** (Lazy API, `scan_parquet`):
* Прочитайте `orders.parquet` и `customers.parquet`.
* Уберите заказы с пропуском в `amount`, оставьте только `amount > 100`.
* Добавьте столбец `month` - номер месяца из `order_dt`.
* Присоедините клиентов (`INNER JOIN` по `customer_id`).
* Сгруппируйте по `region` и `category`: `revenue` (сумма), `avg_check` (среднее), `orders_count`, `unique_customers`.
* Для каждого региона оставьте 3 категории с наибольшей выручкой, сортировка по `region`, затем по `revenue` по убыванию.

Затем:
* Проверьте, что результаты pandas и Polars совпадают (с допуском на ошибки `float`).
* Замерьте время (медиана из 3 запусков) и память таблицы заказов.
* В `markdown` ячейке напишите выводы (4-6 предложений): во сколько раз Polars быстрее (или медленнее), почему, и в каком случае вы выберете pandas.

**Примеры**
```text
region    category     revenue  avg_check  orders_count  unique_customers
Москва    электроника  ...      ...        ...           ...
Москва    еда          ...      ...        ...           ...
Москва    одежда       ...      ...        ...           ...
Поволжье  ...
```

| Вариант | Время, с | Память, МБ |
|---|---|---|
| pandas | ... | ... |
| Polars (lazy) | ... | ... |

**Подсказка**
* Пропуск в pandas - `NaN`, в Polars - `null` (используйте `is_not_null()`).
* Агрегации одного столбца в Polars называйте через `.alias(...)`.
* `group_by` в Polars не гарантирует порядок строк - сортируйте явно.
* Память: `df.memory_usage(deep=True).sum()` в pandas и `df.estimated_size()` в Polars.