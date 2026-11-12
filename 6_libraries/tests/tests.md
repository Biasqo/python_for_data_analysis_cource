# Контрольная работа: AsyncIO, pandas и Polars

```text
Каждое задание оценивается в **4 балла**
```
---
#### 1. Опрос сервисов с таймаутом

Нужно конкурентно проверить 6 сервисов. Сервис, не ответивший за 2.0 секунды, считается недоступным. \
Результаты выводятся **по мере готовности**, а не в порядке списка.

```python
import asyncio
import time

SERVICES = {"auth": 0.4, "billing": 1.2, "catalog": 0.7,
            "search": 2.5, "recommend": 0.9, "notify": 3.0}


async def ping(name: str, latency: float) -> str:
    await asyncio.sleep(latency)
    return f"{name}: OK"
```

**Задание**
* Напишите `async def check(name, latency, timeout=2.0)`: вызывает `ping` с ограничением по времени и возвращает `(name, "OK")` или `(name, "TIMEOUT")`. Исключение наружу не пробрасывать.
* В `main()` запустите все проверки конкурентно и выводите каждый результат сразу после готовности.
* В конце выведите словарь `{имя: статус}` и общее время работы.
* Ответьте: сколько заняла бы последовательная проверка с тем же таймаутом? Зачем `check` возвращает имя сервиса?

**Примеры**
```text
0.4s  auth       OK
0.7s  catalog    OK
0.9s  recommend  OK
1.2s  billing    OK
2.0s  search     TIMEOUT
2.0s  notify     TIMEOUT
{'auth': 'OK', 'billing': 'OK', ..., 'notify': 'TIMEOUT'}   всего: 2.0 с
```

**Подсказка**
Используйте `asyncio.wait_for` и `asyncio.as_completed`. `as_completed` отдаёт результаты в порядке готовности, а не в порядке списка.

#### 2. Найди ошибки

Программа загружает 5 пользователей, считает рейтинг и отправляет письма. Она работает медленно, а письма не отправляются.

```python
import asyncio
import time


async def load_user(user_id):
    time.sleep(1)
    return {"id": user_id, "name": f"user{user_id}"}


async def calc_score(user):
    total = 0
    for i in range(5_000_000):
        total += i % (user["id"] + 1)
    return total


async def send_email(user):
    await asyncio.sleep(0.5)
    if user["id"] == 3:
        raise RuntimeError("SMTP error")
    print("sent to", user["name"])


async def main():
    start = time.perf_counter()

    users = []
    for uid in range(1, 6):
        users.append(await load_user(uid))

    scores = []
    for user in users:
        scores.append(await calc_score(user))

    for user in users:
        asyncio.create_task(send_email(user))

    print("done in", round(time.perf_counter() - start, 1), "s")


asyncio.run(main())
```

**Задание**
* Найдите **4 проблемы**: укажите, где она находится и к чему приводит.
* Исправьте код:
    * загрузка пользователей конкурентна (≈1 с вместо 5 с);
    * тяжёлый расчёт не блокирует event loop;
    * все письма отправляются до завершения `main`, ошибка для `user3` обработана и не теряется.
* Ответьте: почему `asyncio.to_thread` не ускорит CPU-расчёт и какой инструмент подойдёт лучше?

**Примеры**
```text
До исправления:      done in 6.1 s      (писем нет)

После исправления:   sent to user1
                     sent to user2
                     sent to user4
                     sent to user5
                     ошибка: RuntimeError('SMTP error')
                     done in ~3 s
```

**Подсказка**
`time.sleep` и тяжёлые циклы блокируют event loop. Для CPU-задач используйте `ProcessPoolExecutor` и `loop.run_in_executor`: функция должна быть обычной (не `async`) функцией верхнего уровня, запуск - под `if __name__ == "__main__":`.

#### 3. pandas и Polars

Дана небольшая выгрузка заказов с «грязными» данными и справочник клиентов.

```python
import pandas as pd
import polars as pl

data = {
    "order_id":  list(range(1, 11)),
    "client_id": [101, 102, 101, 103, 104, 102, 999, 103, 101, 104],
    "category":  ["Еда", " еда", "Электроника", "ЕДА ", "Транспорт",
                  "электроника", "Еда", "транспорт ", "Электроника", "Еда"],
    "amount":    [250.0, 89.5, 1200.0, None, 300.0, None, 150.0, 60.0, 980.0, 410.0],
}
clients = {"client_id": [101, 102, 103, 104],
           "city": ["Москва", "Казань", "Екатеринбург", "Омск"]}

orders_pd, clients_pd = pd.DataFrame(data), pd.DataFrame(clients)
orders_pl, clients_pl = pl.DataFrame(data), pl.DataFrame(clients)
```

**Задание**
Выполните над данными следующие операции сначала на **pandas**, затем на **Polars**. В Polars шаги 1-3 и 5 оформите одной цепочкой Lazy API (`.lazy()` → ... → `.collect()`).
1. Приведите `category` к нижнему регистру и уберите пробелы по краям.
2. Заполните пропуски в `amount` медианой.
3. Добавьте столбец `vat = amount * 1.2`.
4. Сгруппируйте по `category` и посчитайте сумму, среднее и количество по `amount`.
5. Присоедините `clients` через `LEFT JOIN` по `client_id` и выведите заказы без клиента.

Затем заполните таблицу (одна короткая фраза в ячейке):

| | pandas | Polars |
|---|---|---|
| Обозначение пропуска | | |
| Добавление столбца | | |
| Индекс строк / выбор по условию | | |
| Когда выполняется запрос | | |

**Примеры**
```python
# pandas
df["category"] = df["category"].str.strip().str.lower()

# Polars
df = df.with_columns(pl.col("category").str.strip_chars().str.to_lowercase())
```
Ожидаемый результат шага 5: одна строка - `order_id=7, client_id=999, city=null`.

**Подсказка**
pandas выполняет операции сразу и меняет таблицу на месте. Polars неизменяем: используйте `with_columns` и выражения `pl.col(...)`, а Lazy API выполняет запрос только при вызове `.collect()`.