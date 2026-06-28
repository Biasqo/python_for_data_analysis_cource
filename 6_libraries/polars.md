# Занятие 9. Polars: современная альтернатива pandas
**Блок 6 — Библиотеки | Продолжительность: 90 минут | Уровень: Средний/Продвинутый**

---

## Цели обучения

К концу занятия студенты смогут:
1. Объяснить, в каких ситуациях pandas уступает Polars.
2. Писать запросы в Eager и Lazy API Polars.
3. Использовать API выражений (`pl.col(...)`) для фильтрации, группировки и выбора.
4. Переписать pandas-pipeline на Polars (lazy API).

---

## Поминутный план

### 0–15 | Мотивация: где pandas "ломается"

#### Ограничения pandas

```python
# 1. Однопоточность — pandas не использует несколько ядер CPU
# 2. Лишние копии — многие операции создают промежуточные DataFrame в памяти
# 3. GIL — Python Global Interpreter Lock ограничивает параллелизм
# 4. Строки хранятся как Python-объекты — медленно и дорого по памяти

import pandas as pd
import numpy as np
import time

# Сравнение: pandas vs Polars на 10M строк
n = 10_000_000
df_pd = pd.DataFrame({
    "значение": np.random.randn(n),
    "категория": np.random.choice(["A", "B", "C", "D"], n),
})

t0 = time.perf_counter()
результат_pd = df_pd.groupby("категория")["значение"].agg(["mean", "std", "count"])
print(f"pandas groupby: {time.perf_counter() - t0:.2f}с")
# Типично: ~0.8–1.5с на обычном ноутбуке
```

#### Дерево решений: pandas или Polars?

```
Размер данных < 1M строк?
├── Да → pandas (проще, больше учебников)
└── Нет → Размер > RAM или нужна скорость?
           ├── Да → Polars (lazy API) или PySpark (кластер)
           └── Нет, но нужна скорость → Polars (eager API)

Другие факторы:
- Команда знает только pandas? → pandas
- Нужна интеграция с ML (sklearn, PyTorch)? → pandas (или конвертация)
- Новый проект, нет legacy-кода? → рассмотрите Polars
```

---

### 15–50 | Eager vs Lazy API и выражения

#### Установка и базовый синтаксис

```python
# pip install polars

import polars as pl
import numpy as np

# Создание DataFrame
df = pl.DataFrame({
    "страна":    ["Германия", "Франция", "Италия", "Испания"],
    "ввп":       [4.07, 2.78, 2.10, 1.77],
    "инфляция":  [2.1, 2.5, 3.0, 3.5],
    "население": [83.2, 67.8, 59.6, 47.4],
})

print(df)
print(df.schema)      # типы данных (аналог dtypes)
print(df.shape)
print(df.head(2))
```

#### Eager API — выполнение немедленно

```python
# Выбор столбцов
df.select(["страна", "ввп"])
df.select(pl.col("ввп"), pl.col("инфляция"))

# Фильтрация
df.filter(pl.col("ввп") > 2.5)
df.filter((pl.col("ввп") > 2.0) & (pl.col("инфляция") < 3.0))

# Добавление столбца (with_columns — аналог assign в pandas)
df.with_columns(
    (pl.col("ввп") / pl.col("население") * 1000).alias("ввп_на_душу")
)

# Сортировка
df.sort("ввп", descending=True)

# Переименование
df.rename({"ввп": "gdp", "инфляция": "inflation"})
```

#### Lazy API — выполнение только при `.collect()`

```python
# Ленивый фрейм — операции не выполняются, только строится план
lazy = df.lazy()

# Цепочка операций — запрос
query = (
    lazy
    .filter(pl.col("ввп") > 2.0)
    .with_columns(
        (pl.col("ввп") / pl.col("население")).alias("ввп_на_душу")
    )
    .sort("ввп_на_душу", descending=True)
    .select(["страна", "ввп", "ввп_на_душу"])
)

# Polars оптимизирует план перед выполнением
print(query.explain())  # показать план выполнения

# Выполнить!
результат = query.collect()
print(результат)
```

#### API выражений — сердце Polars

```python
# pl.col() — ссылка на столбец
# Все выражения ленивые и параллельные

df = pl.read_csv("sales.csv")

# Основные операции
(df.lazy()
    .with_columns([
        # Арифметика
        (pl.col("сумма") * 1.2).alias("сумма_с_ндс"),
        # Строковые операции
        pl.col("категория").str.to_lowercase().alias("кат_lower"),
        # Условие (аналог np.where)
        pl.when(pl.col("сумма") > 1000)
          .then(pl.lit("крупная"))
          .otherwise(pl.lit("малая"))
          .alias("размер"),
        # Дата
        pl.col("дата").str.to_date().alias("дата_dt"),
    ])
    .collect()
)

# Wildcard — применить к нескольким столбцам
(df.lazy()
    .with_columns(
        pl.col(pl.Float64).round(2)  # округлить все Float64-столбцы
    )
    .collect()
)
```

#### Сравнение синтаксиса pandas vs Polars

```python
# ФИЛЬТРАЦИЯ
# pandas:
df_pd[df_pd["сумма"] > 500]
# Polars eager:
df_pl.filter(pl.col("сумма") > 500)
# Polars lazy:
df_pl.lazy().filter(pl.col("сумма") > 500).collect()

# ДОБАВЛЕНИЕ СТОЛБЦА
# pandas:
df_pd["наценка"] = df_pd["сумма"] * 0.1
# Polars (неизменяемый — возвращает новый DataFrame):
df_pl = df_pl.with_columns((pl.col("сумма") * 0.1).alias("наценка"))

# ГРУППИРОВКА
# pandas:
df_pd.groupby("категория")["сумма"].agg(["mean", "sum"])
# Polars:
df_pl.group_by("категория").agg([
    pl.col("сумма").mean().alias("ср_сумма"),
    pl.col("сумма").sum().alias("итого"),
])

# ВЫБОР СТОЛБЦОВ
# pandas:
df_pd[["страна", "ввп"]]
# Polars:
df_pl.select(["страна", "ввп"])
```

---

### 50–75 | Join и groupby в Polars

#### Groupby с несколькими агрегациями

```python
df = pl.read_csv("sales.csv")

итоги = (
    df.group_by(["регион", "категория"])
    .agg([
        pl.col("сумма").sum().alias("выручка"),
        pl.col("сумма").mean().alias("ср_чек"),
        pl.col("сумма").count().alias("кол_сделок"),
        pl.col("сумма").max().alias("макс_чек"),
        pl.col("клиент").n_unique().alias("уник_клиентов"),
    ])
    .sort("выручка", descending=True)
)
print(итоги)
```

#### Join в Polars

```python
транзакции = pl.DataFrame({
    "id":        [1, 2, 3, 4],
    "клиент_id": [101, 102, 101, 103],
    "сумма":     [250, 1200, 89, 500],
})

клиенты = pl.DataFrame({
    "клиент_id": [101, 102, 103],
    "имя":       ["Иванов", "Петрова", "Сидоров"],
    "сегмент":   ["VIP", "Стандарт", "VIP"],
})

# LEFT JOIN
результат = транзакции.join(клиенты, on="клиент_id", how="left")

# INNER JOIN
результат = транзакции.join(клиенты, on="клиент_id", how="inner")

# JOIN с разными именами ключей
результат = транзакции.join(
    клиенты,
    left_on="клиент_id",
    right_on="id",
    how="left"
)
```

#### Производительность: pandas vs Polars

```python
import polars as pl
import pandas as pd
import numpy as np
import time

n = 5_000_000
данные = {
    "значение":  np.random.randn(n),
    "категория": np.random.choice(["A", "B", "C", "D"], n),
    "регион":    np.random.choice(["Север", "Юг", "Запад", "Восток"], n),
}

# pandas
df_pd = pd.DataFrame(данные)
t0 = time.perf_counter()
df_pd.groupby(["категория", "регион"])["значение"].agg(["mean", "std"])
print(f"pandas:  {time.perf_counter() - t0:.3f}с")

# Polars eager
df_pl = pl.DataFrame(данные)
t0 = time.perf_counter()
df_pl.group_by(["категория", "регион"]).agg([
    pl.col("значение").mean(),
    pl.col("значение").std(),
])
print(f"Polars:  {time.perf_counter() - t0:.3f}с")
# Polars обычно в 5–15 раз быстрее на этой задаче
```

#### Типичные ловушки при переходе с pandas

```python
# 1. Polars неизменяем — нельзя менять "на месте"
# НЕПРАВИЛЬНО:
df["новый_столбец"] = df["сумма"] * 2  # TypeError!
# ПРАВИЛЬНО:
df = df.with_columns((pl.col("сумма") * 2).alias("новый_столбец"))

# 2. Нет SettingWithCopyWarning — операции всегда возвращают новый объект

# 3. group_by не гарантирует порядок (в отличие от pandas)
df.group_by("категория").agg(pl.col("сумма").sum())  # порядок непредсказуем
df.group_by("категория").agg(pl.col("сумма").sum()).sort("категория")  # правильно

# 4. Индекс отсутствует — в Polars нет индекса строк
# pandas: df.loc["DE"]  → строка по метке индекса
# Polars: df.filter(pl.col("страна") == "Германия")  → всегда явный фильтр
```

---

### 75–90 | Лабораторная работа: переписываем pipeline на Polars

```python
# Задача: взять pipeline очистки из занятий 7–8 и переписать на Polars lazy API

import polars as pl

# --- Оригинальный pandas-код ---
# df = pd.read_csv("transactions.csv")
# df["Категория"] = df["Категория"].str.strip().str.lower()
# df["Сумма"] = pd.to_numeric(df["Сумма"].str.replace(",", "."), errors="coerce")
# df = df[df["Сумма"] > 0]
# итоги = df.groupby("Категория")["Сумма"].agg(["sum", "mean", "count"])

# --- Аналог на Polars lazy API ---
итоги = (
    pl.scan_csv("transactions.csv")          # scan_csv — ленивое чтение!
    .with_columns([
        pl.col("Категория").str.strip_chars().str.to_lowercase(),
        pl.col("Сумма")
          .str.replace(",", ".")
          .cast(pl.Float64, strict=False),
    ])
    .filter(pl.col("Сумма") > 0)
    .group_by("Категория")
    .agg([
        pl.col("Сумма").sum().alias("итого"),
        pl.col("Сумма").mean().alias("среднее"),
        pl.col("Сумма").count().alias("количество"),
    ])
    .sort("итого", descending=True)
    .collect()                               # выполнить!
)

print(итоги)

# Polars оптимизирует весь запрос перед выполнением:
# - pushdown predicate: фильтр применяется как можно раньше
# - projection pushdown: читаются только нужные столбцы
# - параллельное выполнение агрегаций
```

---

## Проверка понимания

**5 вопросов:**

1. В чём главное преимущество Lazy API перед Eager?
   > Polars оптимизирует весь план запроса целиком — фильтры применяются раньше, читаются только нужные столбцы, задачи выполняются параллельно. Eager выполняет каждую операцию немедленно, без глобальной оптимизации.

2. Как в Polars добавить столбец (аналог `df["новый"] = ...` в pandas)?
   > `df = df.with_columns((pl.col("сумма") * 1.2).alias("сумма_с_ндс"))`. Polars неизменяем — нужно присвоить результат.

3. Почему в Polars нет индекса строк?
   > По дизайну: индекс в pandas часто вызывает путаницу и неявное поведение. В Polars всё через явные столбцы и фильтры — предсказуемее и быстрее.

4. Как написать условный столбец (аналог `np.where`) в Polars?
   > `pl.when(условие).then(значение_если_истина).otherwise(значение_если_ложь).alias("имя")` внутри `.with_columns(...)`.

5. Когда Polars не заменит pandas?
   > При интеграции с ML-библиотеками (sklearn, PyTorch), которые ожидают pandas DataFrame или numpy-массивы; при работе с небольшими датасетами, где разница в скорости незначительна; в командах с большим legacy-кодом на pandas.