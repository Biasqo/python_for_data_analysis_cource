# Домашнее задание 3

```text
Каждое задание оценивается в **4 балла**
```

#### 1. Асинхронный загрузчик страниц

**Описание**

Нужно скачать 20 страниц. \
Часть запросов падает с ошибкой, а сервер разрешает не более 5 одновременных соединений. \
Сетевое взаимодействие имитируется через `asyncio.sleep`. Функцию `fetch` менять нельзя. 

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

**Подсказки**

Используйте семафор для ограничения запросов. Использовать `time.sleep` внутри coroutine нельзя.
Используйте только стандартные библиотеки.

#### 2. Асинхронные HTTP-запросы

Получите текущую температуру в нескольких городах через открытое API Open-Meteo и сравните асинхронный и последовательный подходы. Установка: `pip install httpx`.

```python
import asyncio
import time
import httpx

URL = "https://api.open-meteo.com/v1/forecast"
CITIES = {
    "Moscow": (55.75, 37.62),
    "Berlin": (52.52, 13.41),
    "Tokyo": (35.68, 139.69),
    "New York": (40.71, -74.01),
}
```

**Задание**
Напишите:
1. Функцию `fetch_temp(client, city, lat, lon)` - делает `GET` запрос на `URL` с параметрами `latitude`, `longitude` и `current="temperature_2m"` (передайте их через `params=`), проверяет статус через `raise_for_status()`, возвращает `(city, температура)`. Температура лежит в `json["current"]["temperature_2m"]`.
2. `run(cities)` - замеряет время, открывает `httpx.AsyncClient()` через `async with`, внутри `TaskGroup` создаёт задачу `fetch_temp` для каждого города. После выхода из `TaskGroup` печатает `city: temp °C` и время работы.
3. `run_sequential(cities)` - то же самое, но запросы идут по очереди, без `TaskGroup`.
4. Запустите `run(CITIES)` и `run_sequential(CITIES)`.
5. В `markdown`-ячейке или комментарии ответьте: во сколько раз асинхронная версия быстрее и почему?

**Пример вывода** (числа и время будут отличаться)

```text
run(CITIES):
Moscow: 8.3 °C
...
time 0.4

run_sequential(CITIES):
Moscow: 8.3 °C
...
time 1.5
```

**Подсказки**

* Документация Open-Meteo: https://open-meteo.com/en/docs
* API - это обычный адрес в интернете. При отправка на него запроса, в ответ вы получите данные в формате JSON. В Python его можно прочитать как словарь: `response.json()`.
* Параметры запроса передаются в `params=`: `client.get(URL, params={"latitude": lat, "longitude": lon, "current": "temperature_2m"})`. Библиотека сама допишет их к адресу после `?`.
* Чтобы увидеть, как выглядит ответ, откройте в браузере `https://api.open-meteo.com/v1/forecast?latitude=40.18&longitude=44.51&current=temperature_2m`. Температура лежит в `["current"]["temperature_2m"]`.
* Справка по `httpx` (асинхронный клиент, `params=`, `raise_for_status()`): https://www.python-httpx.org/async/
* Результат задачи берите через `.result()` после выхода из `TaskGroup`.

#### 3. Работа с данными

Постройте отчёт «топ-3 категории по выручке в каждом регионе» на **pandas** и на **Polars** и сравните их. 
Потребуется установка: `pip install pandas polars numpy pyarrow`.

Генерация тестовых данных:
```python
from pathlib import Path
import numpy as np
import pandas as pd

N = 10_000_000
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
    "region": rng.choice(["Москва", "Урал", "Сибирь", "Юг", "Поволжье"], 50_000),
})

orders.to_parquet("orders.parquet", index=False)
customers.to_parquet("customers.parquet", index=False)
```

**Задание**
* Прочитайте оба файла, уберите заказы без `amount` и оставьте только `amount > 100`.
* Заджойните клиентов по `customer_id`. (в пандас это `merge` в поларсе `join`)
* Сгруппируйте по `region` и `category`: `revenue` (сумма), `avg_check` (среднее), `orders_count`.
* Для каждого региона оставьте 3 категории с наибольшей выручкой.
* Сделайте это на pandas и на Polars, проверьте, что результаты совпадают.
* Замерьте время каждого варианта.
* В `markdown` ячейке напишите вывод (3-4 предложения): какой вариант быстрее и почему.

**Примеры**
```text
region    category     revenue  avg_check  orders_count
Москва    электроника  ...      ...        ...
Москва    еда          ...      ...        ...
Москва    одежда       ...      ...        ...
Поволжье  ...
```

**Подсказки**

Пропуск в pandas - `NaN`, в Polars - `null`. 
Порядок строк после `group_by` в Polars не гарантирован, сортируйте явно.