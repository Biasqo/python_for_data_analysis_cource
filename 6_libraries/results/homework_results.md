# Домашнее задание 3. Решение

## Задание 1. Асинхронный загрузчик страниц

### Идея решения

- `fetch_with_retry` повторяет `fetch` при `FetchError`. Между попытками стоит `await asyncio.sleep(delay)`, а не `time.sleep`, иначе заблокируется весь event loop. После последней неудачной попытки исключение пробрасывается дальше.
- `download_all` запускает все загрузки сразу через `asyncio.gather`, а число одновременных запросов ограничивает `asyncio.Semaphore(limit)`.
- `gather(..., return_exceptions=True)` возвращает результаты **в порядке `urls`**. Упавшие загрузки приходят как объекты исключений, и одна ошибка не ломает остальные.
- Счётчик активных запросов `active` увеличивается при входе в семафор и уменьшается при выходе. Максимум, до которого он дорос, и есть «пик».
- Для сравнения со «строго последовательной» загрузкой есть отдельная функция `download_sequential`. Она не использует семафор и `gather`.

### Код

```python
import asyncio
import random
import time

random.seed(7)
URLS = [f"https://example.com/page/{i}" for i in range(1, 21)]

class FetchError(Exception):
    pass

async def fetch(url: str) -> str:          # менять нельзя
    await asyncio.sleep(random.uniform(0.3, 1.0))
    if random.random() < 0.25:
        raise FetchError(f"Ошибка при загрузке {url}")
    return f"<html>{url}</html>"


async def fetch_with_retry(url, retries=3, delay=0.2):
    """Всего `retries` попыток. После последней неудачной пробрасывает FetchError."""
    for attempt in range(1, retries + 1):
        try:
            return await fetch(url)
        except FetchError:
            if attempt == retries:
                raise
            await asyncio.sleep(delay)      # НЕ time.sleep!


async def download_all(urls, limit=5):
    sem = asyncio.Semaphore(limit)
    active = 0      # сколько запросов выполняется прямо сейчас
    peak = 0        # максимум за всё время

    async def worker(url):
        nonlocal active, peak
        async with sem:                     # не более `limit` внутри блока
            active += 1
            peak = max(peak, active)
            try:
                return await fetch_with_retry(url)
            finally:
                active -= 1

    results = await asyncio.gather(
        *(worker(u) for u in urls),
        return_exceptions=True,             # ошибки возвращаются как значения
    )
    return results, peak                    # порядок совпадает с urls


async def download_sequential(urls):
    results = []
    for u in urls:
        try:
            results.append(await fetch_with_retry(u))
        except FetchError as e:
            results.append(e)
    return results


def report(results):
    failed = sum(isinstance(r, Exception) for r in results)
    return len(results) - failed, failed


async def main():
    for limit in (1, 5, 20):
        random.seed(7)                      # одинаковый старт для честного сравнения
        t = time.perf_counter()
        results, peak = await download_all(URLS, limit)
        dt = time.perf_counter() - t
        ok, bad = report(results)
        print(f"limit={limit:>2}: загружено {ok}, упало {bad}, "
              f"пик {peak}, время {dt:.1f} с")

    random.seed(7)
    t = time.perf_counter()
    results = await download_sequential(URLS)
    dt = time.perf_counter() - t
    ok, bad = report(results)
    print(f"последовательно: загружено {ok}, упало {bad}, время {dt:.1f} с")

asyncio.run(main())          # в Jupyter: await main()
```

### Результат запуска

```text
limit= 1: загружено 20, упало 0, пик 1, время 19.3 с
limit= 5: загружено 18, упало 2, пик 5, время 4.5 с
limit=20: загружено 19, упало 1, пик 20, время 2.8 с
последовательно: загружено 20, упало 0, время 19.3 с
```

### Выводы

- Время падает почти линейно с ростом `limit`: 19.3 с → 4.5 с → 2.8 с. Страницы грузятся независимо, а ожидание сети (`sleep`) не занимает процессор.
- `limit=1` по времени совпадает с последовательной загрузкой, потому что это и есть последовательная загрузка.
- При `limit=20` время почти не уменьшается по сравнению с `limit=5`, потому что его определяют самые долгие запросы с ретраями.
- Число упавших страниц у разных запусков разное. `fetch` берёт числа из общего генератора `random`, а при конкурентной работе порядок вызовов меняется. Падают только те страницы, у которых все 3 попытки оказались неудачными.
- Пик одновременных запросов всегда равен `limit` (когда URL больше `limit`), и именно это гарантирует семафор.

---

## Задание 2. Асинхронные HTTP-запросы

### Идея решения

- `fetch_temp` делает `await client.get(...)` с параметрами через `params=`, проверяет статус и достаёт температуру из JSON.
- `run` открывает один общий `AsyncClient` и в `TaskGroup` создаёт по задаче на город. Все запросы идут одновременно.
- Результаты берутся через `task.result()` **после** выхода из `async with TaskGroup()`. К этому моменту все задачи гарантированно завершены.
- `run_sequential` делает те же запросы по очереди, с `await` на каждом.

### Код

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


async def fetch_temp(client, city, lat, lon):
    response = await client.get(
        URL,
        params={"latitude": lat, "longitude": lon, "current": "temperature_2m"},
    )
    response.raise_for_status()
    return city, response.json()["current"]["temperature_2m"]


async def run(cities):
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(fetch_temp(client, city, lat, lon))
                for city, (lat, lon) in cities.items()
            ]
    # сюда доходим, когда все задачи завершены
    for task in tasks:
        city, temp = task.result()
        print(f"{city}: {temp} °C")
    print(f"time {time.perf_counter() - start:.1f}")


async def run_sequential(cities):
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        for city, (lat, lon) in cities.items():
            city, temp = await fetch_temp(client, city, lat, lon)
            print(f"{city}: {temp} °C")
    print(f"time {time.perf_counter() - start:.1f}")


async def main():
    print("run(CITIES):")
    await run(CITIES)
    print("\nrun_sequential(CITIES):")
    await run_sequential(CITIES)

asyncio.run(main())          # в Jupyter: await main()
```

> Нужен Python 3.11+, потому что `asyncio.TaskGroup` появился в 3.11.

### Пример вывода

(Числа условные: этот код я не запускал, из моей среды нет доступа к Open-Meteo. Погода и время у вас будут свои.)

```text
run(CITIES):
Moscow: 8.3 °C
Berlin: 11.0 °C
Tokyo: 17.5 °C
New York: 9.8 °C
time 0.4

run_sequential(CITIES):
Moscow: 8.3 °C
Berlin: 11.0 °C
Tokyo: 17.5 °C
New York: 9.8 °C
time 1.5
```

### Ответ на вопрос

Асинхронная версия быстрее примерно в 3-4 раза, то есть примерно во столько, сколько городов (4). Сам запрос почти целиком состоит из ожидания ответа от сервера по сети, а процессор в это время простаивает. В последовательной версии ожидания **складываются**: `t1 + t2 + t3 + t4`. В асинхронной все 4 запроса отправляются сразу, пока ждём первый ответ, и общее время примерно равно времени **самого долгого** запроса: `max(t1, t2, t3, t4)`. Ускорение не точно 4×, потому что у запросов есть накладные расходы (установка соединения, разное время ответа).

---

## Задание 3. Работа с данными

### Идея решения

Один и тот же пайплайн в двух библиотеках:

1. Прочитать два parquet-файла.
2. Убрать заказы с пропуском в `amount` и оставить `amount > 100`.
3. Присоединить клиентов по `customer_id` (в pandas `merge`, в Polars `join`).
4. Сгруппировать по `region` и `category`: `revenue` (сумма), `avg_check` (среднее), `orders_count` (количество).
5. Оставить топ-3 категории по выручке в каждом регионе.

Особенности:

- **pandas**: `dropna` убирает `NaN`. Топ-3 получаем так: сортируем по `region` и `revenue` по убыванию, затем `groupby("region").head(3)`.
- **Polars**: используется ленивый режим (`scan_parquet` + `collect`), он оптимизирует запрос целиком (например, читает только нужные столбцы). Топ-3 берём через оконную функцию: `rank(...).over("region") <= 3`. После `group_by` порядок строк не гарантирован, поэтому в конце явная `sort`.
- Для сравнения результат Polars переводится в pandas, и дальше `pd.testing.assert_frame_equal` сравнивает таблицы с допуском на ошибки `float` (`rtol`) и без проверки типов (в pandas `int64`, в Polars `UInt32`).
- Время: медиана из 3 запусков.

### Код

```python
from pathlib import Path
import time
import statistics
import numpy as np
import pandas as pd
import polars as pl

# ---------- генерация данных (из условия) ----------
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


# ---------- pandas ----------
def with_pandas():
    o = pd.read_parquet("orders.parquet")
    c = pd.read_parquet("customers.parquet")

    o = o.dropna(subset=["amount"])
    o = o[o["amount"] > 100]

    df = o.merge(c, on="customer_id")                    # inner join

    g = (
        df.groupby(["region", "category"], as_index=False)
          .agg(revenue=("amount", "sum"),
               avg_check=("amount", "mean"),
               orders_count=("amount", "count"))
    )

    g = g.sort_values(["region", "revenue"], ascending=[True, False])
    return g.groupby("region").head(3).reset_index(drop=True)


# ---------- Polars (lazy) ----------
def with_polars():
    o = pl.scan_parquet("orders.parquet")
    c = pl.scan_parquet("customers.parquet")

    return (
        o.filter(pl.col("amount").is_not_null() & (pl.col("amount") > 100))
         .join(c, on="customer_id", how="inner")
         .group_by("region", "category")
         .agg(
             pl.col("amount").sum().alias("revenue"),
             pl.col("amount").mean().alias("avg_check"),
             pl.len().alias("orders_count"),
         )
         # ранг категории по выручке внутри региона, оставляем топ-3
         .filter(pl.col("revenue").rank("ordinal", descending=True).over("region") <= 3)
         .sort(["region", "revenue"], descending=[False, True])   # порядок после group_by не гарантирован
         .collect()
         .to_pandas()          # для сравнения с pandas
    )


# ---------- замер времени: медиана из 3 запусков ----------
def bench(func, runs=3):
    times = []
    for _ in range(runs):
        t = time.perf_counter()
        result = func()
        times.append(time.perf_counter() - t)
    return result, statistics.median(times)


res_pd, t_pd = bench(with_pandas)
res_pl, t_pl = bench(with_polars)

# ---------- проверка совпадения ----------
pd.testing.assert_frame_equal(res_pd, res_pl, check_dtype=False, rtol=1e-9)
print("Результаты pandas и Polars совпадают")

print(res_pd)
print(f"\npandas: {t_pd:.2f} с")
print(f"Polars: {t_pl:.2f} с  (быстрее в {t_pd / t_pl:.1f} раз)")
```

### Пример результата

Я проверил код на уменьшенных данных (`N = 2_000_000`), числа на ваших 10 млн строк будут другими:

```text
Результаты pandas и Polars совпадают
     region     category      revenue   avg_check  orders_count
0    Москва        книги  62331052.47  819.994376         76014
1    Москва  электроника  62314668.25  823.723308         75650
2    Москва    транспорт  62143869.10  820.381110         75750
3  Поволжье    транспорт  63107857.49  820.979296         76869
4  Поволжье  электроника  62959329.07  819.548164         76822
5  Поволжье          еда  62840706.62  820.728338         76567
...

pandas: 0.67 с
Polars: 0.18 с  (быстрее в 3.7 раз)
```

Выручки по категориям внутри региона очень близки, так как данные случайные, а категории равновероятны. Поэтому состав топ-3 у вас может отличаться от моего.

### Вывод (для markdown-ячейки)

Polars оказался быстрее pandas примерно в 3-4 раза (на 10 млн строк разница, скорее всего, будет не меньше). Причин несколько. Polars написан на Rust и распараллеливает чтение parquet, фильтрацию, join и агрегации по всем ядрам, а pandas выполняет большую часть операций в одном потоке. Кроме того, ленивый режим (`scan_parquet`) строит план запроса и оптимизирует его целиком: читает только нужные столбцы (`order_dt` и `order_id` не нужны) и применяет фильтр как можно раньше. В pandas каждая строка кода выполняется сразу, и все столбцы загружаются в память. Результаты обеих библиотек совпали, то есть выбор между ними влияет на скорость, а не на корректность.

---

## Как запустить

```bash
pip install httpx pandas polars numpy pyarrow
```

Нужен Python 3.11 или новее (для `asyncio.TaskGroup`). В Jupyter вместо `asyncio.run(main())` пишите `await main()`.