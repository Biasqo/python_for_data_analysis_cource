# Глава 6. От pandas к Polars и PySpark: работа с табличными данными

## Часть 1. NumPy and Pandas

### NumPy

NumPy - это фундаментальная библиотека для научных вычислений в Python.

Она нужна везде, где есть числа: анализ данных, машинное обучение, физика, инженерия, финансы, обработка изображений.

На чём основан:
- Написан на C и Fortran - поэтому работает очень быстро.
- Внутри - многомерные массивы (ndarray), которые хранятся в памяти непрерывно, как в C.
- Это позволяет выполнять операции без циклов Python (векторизация).

Зачем нужен:
- Главная структура - однородный массив (все элементы одного типа).
- Векторные операции: сложение, умножение и т.д. выполняются сразу над всеми элементами.
- Broadcasting - автоматическое выравнивание массивов разной формы.
- Огромный набор математических функций (sin, cos, exp, log, статистика, линейная алгебра, БПФ).
- Работа с осями (axis) - можно агрегировать по строкам, столбцам или по всем измерениям.
- Генерация случайных данных (rand, randn, randint, seed).

Ключевые возможности:
- Срезы, индексация, булевы маски.
- Изменение формы (reshape, flatten, transpose).
- Объединение (vstack, hstack).
- Работа с пропусками (np.nan, isnan, nanmean).
- Линейная алгебра (умножение, обратная матрица, собственные числа, решение систем).

Особенности:
- Массивы фиксированного размера (нельзя добавлять элементы как в список).
- Все операции создают новые массивы (не изменяют исходные, если явно не указано).
- Индексация начинается с 0.
- При смешивании типов данные приводятся к более общему (int → float).

### Series и DataFrame

`Pandas` - основная библиотека Python для работы с табличными данными.

Под капотом NumPy - это даёт скорость и интеграцию с энтерпрайзом.

Две главные структуры:
1) Series - одномерный массив с метками (индексом). Своего рода столбец в таблице.
2) DataFrame - двумерная таблица: строки + столбцы с метками.

Индексация:
- В Series и DataFrame у каждой строки есть индекс (метка).
- Индекс может быть числовым, строковым, датой и т.д.
- Доступ по метке работает через .loc[] (по имени) и .iloc[] (по позиции).

Выравнивание:
- При арифметике (сложение, вычитание и т.д.) данные выравниваются по индексу автоматически.
- Это ключевая фишка pandas: не нужно заботиться о порядке строк.

Основные возможности:
- Загрузка и сохранение данных (CSV, Excel, SQL, JSON, Parquet).
- Просмотр и описание данных (головы, хвосты, типы, статистика).
- Выборка строк и столбцов (по имени, по позиции, по условию).
- Фильтрация с помощью булевых масок.
- Добавление, удаление, переименование столбцов.
- Сортировка по одному или нескольким столбцам.
- Группировка и агрегация (groupby, pivot_table).
- Объединение таблиц (concat, merge - как JOIN в SQL).
- Работа с пропусками (удалить, заполнить).
- Работа с датами и временными рядами.
- Применение функций к элементам, столбцам, строкам.
- Иерархические индексы (MultiIndex).

Особенности:
- Индексы автоматически выравниваются при операциях.
- Пропуски (NaN) не ломают вычисления.
- Поддерживаются большие объёмы данных (но не безгранично).
- Многие операции возвращают копию, а не изменяют исходные данные.

### IO

*Чтение*
---
```python
pd.read_csv(путь, sep=',', header='infer', names=None,
            index_col=None, usecols=None, dtype=None, parse_dates=False,
            na_values=None, chunksize=None, encoding=None,
            skiprows=None, nrows=None, compression='infer')

pd.read_excel(путь, sheet_name=0, header=0, names=None,
              index_col=None, usecols=None, dtype=None, na_values=None)

pd.read_json(путь, orient='index', typ='frame', lines=False,
             encoding=None, compression='infer')

pd.read_parquet(путь, columns=None, engine='auto',
                filters=None, storage_options=None)

pd.read_sql(sql, соединение, index_col=None, parse_dates=None,
            columns=None, chunksize=None)

pd.read_clipboard(sep='\\s+', header='infer', dtype=None)

pd.read_feather(путь, columns=None, use_threads=True)

pd.read_hdf(путь, key=None, mode='r', columns=None)

pd.read_pickle(путь, compression='infer')

pd.read_html(источник, match='.+', flavor=None, header=None, index_col=None,
             encoding=None, displayed_only=True)

pd.read_xml(путь, xpath='.//*', namespaces=None, encoding='utf-8')
```

*Запись*
---
```python
df.to_csv(путь, sep=',', na_rep='', float_format=None,
          columns=None, header=True, index=True, index_label=None,
          mode='w', encoding='utf-8', compression='infer',
          quoting=None, quotechar='"', chunksize=None,
          date_format=None, decimal='.')

df.to_excel(путь, sheet_name='Лист1', na_rep='', float_format=None,
            columns=None, header=True, index=True, index_label=None,
            startrow=0, startcol=0, engine=None, merge_cells=True)

df.to_json(путь, orient='index', date_format='epoch',
           double_precision=10, force_ascii=True, date_unit='ms',
           default_handler=None, lines=False, compression='infer',
           indent=None)

df.to_parquet(путь, engine='auto', compression='snappy',
              index=True, partition_cols=None, storage_options=None)

df.to_sql(имя_таблицы, соединение, schema=None, if_exists='fail',
          index=True, index_label=None, chunksize=None, dtype=None,
          method=None)

df.to_pickle(путь, compression='infer', protocol=4)

df.to_feather(путь, compression='lz4', compression_level=None)

df.to_hdf(путь, key, mode='a', format=None, append=False,
          data_columns=None, index=None)

df.to_markdown(путь, mode='wt', index=True, tablefmt='pipe')

df.to_latex(путь, header=True, index=True, longtable=False,
            escape=True, bold_rows=False, column_format=None)

df.to_stata(путь, convert_dates=None, write_index=True,
            encoding='utf-8', version=117)
```

*Вспомогательные*
```python
pd.options.display.max_rows = 100          # настройки вывода
pd.options.display.max_columns = None
pd.set_option('display.float_format', '{:.2f}'.format)

df.info(verbose=True, memory_usage=True)   # сводка по колонкам
df.dtypes                                   # типы данных
df.memory_usage(deep=True)                  # память на колонку

pd.concat([df1, df2], ignore_index=True)   # объединение частей
```

### Индексация, фильтрация, `.copy()`

Доступ к данным
---
# loc - по меткам индекса (ВКЛЮЧАЕТ правую границу)
df.loc[строка, столбец]
df.loc["DE", "ввп"]                           # одна ячейка
df.loc["DE":"FR", "ввп":"население"]          # срез строк и столбцов (включая границы)
df.loc[:, ["ввп", "население"]]               # все строки, выбранные столбцы
df.loc[["DE", "FR", "IT"]]                    # выбранные строки, все столбцы

# iloc - по позициям (НЕ ВКЛЮЧАЕТ правую границу, как в Python)
df.iloc[строка, столбец]
df.iloc[0, 1]                                 # первая строка, второй столбец
df.iloc[0:3, 0:2]                             # строки 0,1,2; столбцы 0,1 (НЕ включая 3 и 2)
df.iloc[:, [0, 2]]                            # все строки, столбцы на позициях 0 и 2
df.iloc[-5:]                                  # последние 5 строк

# at / iat - быстрый доступ к ОДНОЙ ячейке
df.at["DE", "ввп"]                            # по меткам (быстрее loc)
df.iat[0, 1]                                  # по позициям (быстрее iloc)

# [] - доступ по имени столбца
df["ввп"]                                     # Series (один столбец)
df[["ввп", "население"]]                      # DataFrame (несколько столбцов)
df[0:5]                                       # первые 5 строк (срез по строкам)

*Булевы маски*
---
# Одно условие
df[df["сумма"] > 100]                         # все строки где сумма > 100
df[df["категория"] == "еда"]                  # точное совпадение

# Несколько условий: & (И), | (ИЛИ), ~ (НЕ)
df[(df["сумма"] > 100) & (df["категория"] == "еда")]
df[(df["сумма"] > 100) | (df["категория"] == "транспорт")]
df[~df["категория"].isin(["еда", "транспорт"])]

# isin() - проверка вхождения в список
df[df["категория"].isin(["еда", "транспорт", "развлечения"])]

# between() - проверка диапазона
df[df["сумма"].between(100, 500)]             # 100 <= сумма <= 500

# str методы для текстовых столбцов
df[df["название"].str.contains("пицца", case=False)]  # содержит подстроку
df[df["название"].str.startswith("A")]                # начинается с
df[df["название"].str.endswith("ов")]                 # заканчивается на
df[df["название"].str.len() > 10]                     # длина строки

# isna() / notna() - пропуски
df[df["сумма"].isna()]                        # строки с пропусками
df[df["сумма"].notna()]                       # строки без пропусков

# duplicated() / drop_duplicates()
df[df.duplicated(subset=["id"], keep=False)]  # все дубликаты по id
df.drop_duplicates(subset=["id"], keep="first")  # удалить дубликаты

# nlargest() / nsmallest() - топ N
df.nlargest(5, "сумма")                       # 5 самых больших сумм
df.nsmallest(3, "сумма")                      # 3 самых маленьких сумм

*Запросы - альтернатива*
---
# Простые условия
df.query("сумма > 100")
df.query("категория == 'еда'")
df.query("сумма > 100 and категория == 'еда'")
df.query("сумма > 100 or категория == 'транспорт'")

# Переменные через @
limit = 500
df.query("сумма > @limit")
categories = ["еда", "транспорт"]
df.query("category in @categories")

# Строковые методы в query
df.query("name.str.contains('пицца')")
df.query("name.str.startswith('A')")

# Ссылка на внешние переменные
min_sum = 100
max_sum = 500
df.query("@min_sum <= sum <= @max_sum")

Copy()
---
# ОПАСНО: срез может быть view или copy - pandas не гарантирует
df_еда = df[df["category"] == "еда"]   # может быть view!
df_еда["add"] = df_еда["sum"] * 0.1    # SettingWithCopyWarning!

# ✅ БЕЗОПАСНО: явная копия
df_еда = df[df["категория"] == "еда"].copy()
df_еда["наценка"] = df_еда["сумма"] * 0.1     # НЕТ Warning!

# Другие случаи где нужна копия
df_copy = df.copy()                           # полная копия всего DataFrame
df_copy = df[["ввп", "население"]].copy()     # копия подмножества столбцов
df_copy = df.head(10).copy()                  # копия первых 10 строк

# loc с присваиванием - БЕЗОПАСНО (работает с оригиналом)
df.loc[df["категория"] == "еда", "наценка"] = df["сумма"] * 0.1

# is_copy - проверка является ли DataFrame копией
df._is_copy                                    # None или предупреждение

ВЫБОР СТРОК И СТОЛБЦОВ
---
# sample() - случайная выборка
df.sample(n=10)                               # 10 случайных строк
df.sample(frac=0.1)                           # 10% случайных строк
df.sample(frac=1)                             # перемешать все строки

# head() / tail() - первые/последние строки
df.head(10)                                   # первые 10 строк
df.tail(5)                                    # последние 5 строк

# take() - выбор по позициям
df.take([0, 2, 5])                            # строки на позициях 0,2,5

# filter() - выбор столбцов по имени
df.filter(like="сумма")                       # столбцы содержащие "сумма"
df.filter(regex=r"^ввп")                      # столбцы начинающиеся с "ввп"

# select_dtypes() - выбор по типу данных
df.select_dtypes(include=["int64", "float64"]) # числовые столбцы
df.select_dtypes(exclude=["object"])           # все кроме текстовых

ПОЛЕЗНЫЕ ПРОВЕРКИ
─────────────────────────────────────────────────────────────────
df.shape                                      # (строки, столбцы)
df.columns                                    # список столбцов
df.index                                      # индекс
df["столбец"].unique()                        # уникальные значения
df["столбец"].nunique()                       # количество уникальных
df["столбец"].value_counts()                  # частотность значений
df.isnull().sum()                             # количество пропусков по столбцам

### 35–45 | Столбцы: `.apply()`, `.str`, типы

```python
df["размер"] = df["сумма"].apply(lambda x: "крупная" if x > 1000 else "малая")
# ⚠️ .apply() - цикл Python, медленно на больших данных; предпочитайте векторизацию

df["категория"] = df["категория"].str.strip().str.lower()
df["есть_скидка"] = df["описание"].str.contains("скидка", na=False)

df["amount"] = df["amount"].astype(float)
df["category"] = df["category"].astype# Занятие. От pandas к Polars и PySpark: работа с табличными данными
**Блок 6 - Библиотеки | Продолжительность: 180 минут | Уровень: Средний/Продвинутый**

---

## Цели обучения

К концу занятия студенты смогут:
1. Создавать, читать и записывать DataFrame в pandas (CSV/JSON/Parquet), уверенно применять `loc`/`iloc` и булевы маски.
2. Агрегировать данные через `groupby`/`pivot_table`, объединять таблицы (`merge`/`concat`), работать с датами и пропусками, проводить базовый EDA.
3. Объяснить, в чём Polars превосходит pandas, и писать запросы в Eager и Lazy API с использованием выражений `pl.col(...)`.
4. Объяснить архитектуру Spark (driver/executors/DAG) и выполнять базовые операции DataFrame API и SQL-запросы в PySpark.
5. Осознанно выбирать инструмент (pandas / Polars / PySpark) под размер данных и задачу.

---

## Часть 1. Pandas (0–60 мин)
("category")   # экономит память
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
```

### 45–60 | GroupBy, merge, время, мини-EDA

```python
# Именованные агрегации
итоги = df.groupby("регион").agg(
    выручка=("сумма", "sum"),
    ср_чек=("сумма", "mean"),
    уник_продавцов=("продавец", "nunique"),
)

# transform - результат той же формы (без сворачивания строк)
df["доля_от_региона"] = df["сумма"] / df.groupby("регион")["сумма"].transform("sum")

# pivot_table
сводная = pd.pivot_table(df, values="сумма", index="регион", columns="категория",
                          aggfunc="sum", fill_value=0, margins=True)

# merge - аналог SQL JOIN
df = pd.merge(транзакции, клиенты, on="клиент_id", how="left",
              validate="many_to_one")   # проверка кардинальности связи!
print(df[df["имя"].isna()])   # транзакции без совпавшего клиента

# Даты и скользящие агрегаты
df["дата"] = pd.to_datetime(df["дата"])
df["месяц"] = df["дата"].dt.month
df_ts = df.set_index("дата")
месячные = df_ts["сумма"].resample("M").sum()
df_ts["скол_ср_7д"] = df_ts["сумма"].rolling(window=7).mean()

# Пропуски и выбросы (мини-EDA)
df["сумма"] = df["сумма"].fillna(df["сумма"].median())
Q1, Q3 = df["сумма"].quantile([0.25, 0.75]); IQR = Q3 - Q1
выбросы = df[(df["сумма"] < Q1 - 1.5*IQR) | (df["сумма"] > Q3 + 1.5*IQR)]
```

**Вопросы на закрепление (pandas):**
1. Чем `df.loc[0]` отличается от `df.iloc[0]`? → `loc` ищет метку индекса, `iloc` - позицию.
2. Зачем нужен `.copy()` после среза DataFrame? → срез может быть view, изменение вызовет `SettingWithCopyWarning`.
3. Чем `groupby().agg()` отличается от `groupby().transform()`? → `agg` сворачивает группы, `transform` сохраняет исходную форму.
4. Когда предпочесть Parquet вместо CSV? → для больших данных, читаемых кодом: быстрее, компактнее, сохраняет типы.

---

## Часть 2. Polars (60–120 мин)

### 60–70 | Мотивация: где pandas "ломается"

pandas: однопоточность, лишние копии в памяти, GIL, строки как Python-объекты. На 10M строк `groupby` в pandas занимает ~0.8–1.5с; Polars за счёт параллелизма и Rust-ядра обычно **в 5–15 раз быстрее**.

```
Размер данных < 1M строк? → pandas (проще)
Размер > RAM или нужна скорость? → Polars (lazy) или PySpark (кластер)
Нужна скорость, данные помещаются в RAM? → Polars (eager)
Нужна интеграция с ML (sklearn/PyTorch)? → pandas
```

### 70–90 | Eager vs Lazy API, выражения

```python
import polars as pl

df = pl.DataFrame({
    "страна": ["Германия", "Франция", "Италия", "Испания"],
    "ввп": [4.07, 2.78, 2.10, 1.77],
    "население": [83.2, 67.8, 59.6, 47.4],
})

# Eager - выполняется немедленно
df.filter(pl.col("ввп") > 2.5)
df.with_columns((pl.col("ввп") / pl.col("население") * 1000).alias("ввп_на_душу"))

# Lazy - строит план, выполняется только на .collect()
query = (
    df.lazy()
    .filter(pl.col("ввп") > 2.0)
    .with_columns((pl.col("ввп") / pl.col("население")).alias("ввп_на_душу"))
    .sort("ввп_на_душу", descending=True)
    .select(["страна", "ввп", "ввп_на_душу"])
)
print(query.explain())     # план выполнения (pushdown predicate, projection pushdown)
результат = query.collect()

# API выражений - условие (аналог np.where), строки, даты
(df.lazy().with_columns([
    pl.col("категория").str.to_lowercase().alias("кат_lower"),
    pl.when(pl.col("сумма") > 1000).then(pl.lit("крупная")).otherwise(pl.lit("малая")).alias("размер"),
]).collect())
```

**Синтаксис pandas ↔ Polars:**

| Операция | pandas | Polars |
|---|---|---|
| Фильтр | `df[df["сумма"]>500]` | `df.filter(pl.col("сумма")>500)` |
| Новый столбец | `df["x"]=df["сумма"]*0.1` | `df.with_columns((pl.col("сумма")*0.1).alias("x"))` |
| Группировка | `df.groupby("к")["с"].agg(["mean"])` | `df.group_by("к").agg(pl.col("с").mean())` |

### 90–105 | GroupBy и Join в Polars

```python
итоги = (
    df.group_by(["регион", "категория"])
    .agg([
        pl.col("сумма").sum().alias("выручка"),
        pl.col("сумма").mean().alias("ср_чек"),
        pl.col("клиент").n_unique().alias("уник_клиентов"),
    ])
    .sort("выручка", descending=True)
)

результат = транзакции.join(клиенты, on="клиент_id", how="left")   # left/inner/right
```

### 105–120 | Ловушки при переходе с pandas + лаборатория

```python
# 1. Polars неизменяем - нельзя менять "на месте"
df = df.with_columns((pl.col("сумма") * 2).alias("новый_столбец"))   # НЕ df["новый"]=...

# 2. group_by не гарантирует порядок - сортируйте явно при необходимости
# 3. Индекса строк нет - только явные фильтры

# Переписываем pandas-pipeline на Polars lazy API
итоги = (
    pl.scan_csv("transactions.csv")                 # ленивое чтение
    .with_columns([
        pl.col("Категория").str.strip_chars().str.to_lowercase(),
        pl.col("Сумма").str.replace(",", ".").cast(pl.Float64, strict=False),
    ])
    .filter(pl.col("Сумма") > 0)
    .group_by("Категория")
    .agg([pl.col("Сумма").sum().alias("итого"), pl.col("Сумма").mean().alias("среднее")])
    .sort("итого", descending=True)
    .collect()
)
```

**Вопросы на закрепление (Polars):**
1. Главное преимущество Lazy API? → глобальная оптимизация плана (pushdown фильтров/проекций, параллелизм).
2. Как добавить столбец в Polars? → `df = df.with_columns(expr.alias("имя"))` - Polars неизменяем.
3. Аналог `np.where` в Polars? → `pl.when(...).then(...).otherwise(...)`.
4. Когда Polars не заменит pandas? → интеграция с ML-библиотеками, маленькие датасеты, legacy-код на pandas.

---

## Часть 3. PySpark (120–180 мин)

### 120–135 | Зачем Spark и архитектура

```
Данные помещаются в RAM одной машины (< 100 ГБ)? → Polars/pandas
Данные распределены по кластеру? → PySpark (или Dask); нужен кластер (EMR/Dataproc/Databricks)
```

Архитектура: **Driver** (строит DAG, координирует) → **Executors** (JVM-процессы на узлах, выполняют задачи над **партициями**). **Shuffle** - перераспределение данных между узлами по сети - самая дорогая операция.

Как и в Polars lazy: **трансформации** (`filter`, `select`, `withColumn`) ленивы и строят DAG; **действия** (`show`, `collect`, `count`, `write`) запускают выполнение.

### 135–150 | DataFrame API

```python
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder.appName("Анализ").master("local[*]")
         .config("spark.driver.memory", "4g").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

df = spark.read.option("header", "true").option("inferSchema", "true").csv("transactions.csv")

# Трансформации
df = df.withColumn("ввп_млрд", F.col("ввп") * 1000)
df = (df
    .withColumn("сумма_с_ндс", F.col("сумма") * 1.2)
    .withColumn("размер", F.when(F.col("сумма") > 1000, "крупная")
                            .when(F.col("сумма") > 100, "средняя")
                            .otherwise("малая"))
    .withColumn("категория", F.lower(F.trim(F.col("категория"))))
    .fillna({"сумма": 0.0, "категория": "неизвестно"})
)

# Действия
df.show(5); df.count(); df.printSchema()
# ⚠️ df.collect() опасен на большом кластере - переносит все данные на driver
```

### 150–165 | GroupBy, Join, SQL

```python
итоги = df.groupBy("регион", "категория").agg(
    F.sum("сумма").alias("выручка"),
    F.avg("сумма").alias("ср_чек"),
    F.countDistinct("клиент_id").alias("уник_клиентов"),
).orderBy(F.col("выручка").desc())

# Оконные функции
from pyspark.sql.window import Window
окно = Window.partitionBy("регион").orderBy(F.col("сумма").desc())
df = df.withColumn("ранг_в_регионе", F.rank().over(окно))

# Broadcast join - для маленьких таблиц, избегает shuffle
from pyspark.sql.functions import broadcast
результат = транзакции.join(broadcast(клиенты), on="клиент_id", how="left")

# SQL-интерфейс - тот же план выполнения, что и DataFrame API
транзакции.createOrReplaceTempView("транзакции")
spark.sql("""
    SELECT категория, SUM(сумма) AS выручка
    FROM транзакции WHERE сумма > 0
    GROUP BY категория ORDER BY выручка DESC
""").show()
```

### 165–180 | Лабораторная работа: единый pipeline на трёх инструментах

```python
# Одна и та же задача - фильтр → join → группировка → агрегация -
# реализована на pandas, Polars и PySpark. Сравните код и время выполнения.

# PySpark-версия:
результат = (
    транзакции
    .withColumn("категория", F.lower(F.trim(F.col("категория"))))
    .filter(F.col("сумма") > 0)
    .join(broadcast(клиенты), "клиент_id", "left")
    .groupBy("сегмент", "категория")
    .agg(F.sum("сумма").alias("выручка"), F.countDistinct("клиент_id").alias("уник_клиентов"))
    .orderBy(F.col("выручка").desc())
)
результат.show(20, truncate=False)
результат.write.mode("overwrite").parquet("output/итоги_по_сегментам")
spark.stop()
```

**Вопросы на закрепление (PySpark):**
1. Разница между трансформацией и действием? → трансформации ленивы (строят DAG), действия запускают вычисление.
2. Почему `df.collect()` опасен на большом кластере? → переносит все данные на driver, риск OutOfMemoryError.
3. Что такое shuffle? → перераспределение данных между executors по сети; самая медленная операция.
4. Зачем `broadcast()` при join? → рассылает маленькую таблицу на все executors, join выполняется без shuffle.

---

## Итоговое сравнение инструментов

| Критерий | pandas | Polars | PySpark |
|---|---|---|---|
| Размер данных | < 1M–10M строк | до размера RAM одной машины | распределённые, > RAM, кластер |
| Параллелизм | нет (однопоточно) | да, многоядерно | да, кластер |
| Синтаксис | привычный, много туториалов | похож на pandas + выражения | DataFrame API или SQL |
| Ленивые вычисления | нет | опционально (`.lazy()`) | всегда (transform/action) |
| Экосистема ML | лучшая (sklearn, PyTorch) | ограниченная, растёт | Spark MLlib |
| Когда выбрать | прототип, малые данные, legacy | новый проект, скорость на одной машине | terabytes, кластер, продакшн big data |