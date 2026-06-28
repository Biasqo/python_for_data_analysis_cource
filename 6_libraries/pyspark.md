# Занятие 10. PySpark: распределённые вычисления
**Блок 6 — Библиотеки | Продолжительность: 90 минут | Уровень: Продвинутый**

---

## Цели обучения

К концу занятия студенты смогут:
1. Объяснить архитектуру Spark: driver, executors, партиции, DAG.
2. Различать трансформации и действия в Spark.
3. Выполнять базовые операции с DataFrame API (select, filter, withColumn, groupBy, join).
4. Запускать SQL-запросы через `spark.sql()`.

---

## Поминутный план

### 0–20 | Концепции распределённых вычислений

#### Зачем Spark, если есть Polars?

```
Данные помещаются в RAM одной машины (< 100 ГБ)?
├── Да → Polars или pandas (занятия 7–9)
└── Нет → Данные распределены по кластеру?
           ├── Да → PySpark (или Dask)
           └── Нет → Нужен кластер: AWS EMR, GCP Dataproc, Databricks
```

#### Архитектура Spark

```
┌─────────────────────────────────────────────┐
│                 Driver (ваш код)             │
│  SparkSession → строит DAG → планировщик    │
└────────────────────┬────────────────────────┘
                     │ задачи
        ┌────────────┼────────────┐
        ▼            ▼            ▼
  Executor 1    Executor 2    Executor 3
  [Partition 1] [Partition 2] [Partition 3]
  [Partition 4] [Partition 5] [Partition 6]

Ключевые понятия:
- Driver:     ваша программа, строит план, координирует
- Executor:   JVM-процесс на узле кластера, выполняет задачи
- Partition:  кусок данных, единица параллелизма
- DAG:        граф зависимостей между операциями
- Shuffle:    перераспределение данных между узлами (дорогая операция!)
```

#### Ленивые вычисления в Spark

```python
# В pandas — немедленное выполнение:
df["новый"] = df["сумма"] * 1.2   # выполняется сразу

# В Spark — ленивое выполнение:
# Трансформации (filter, select, withColumn) → строят DAG, ничего не выполняют
# Действия (show, collect, count, write) → запускают выполнение DAG

# Аналогия: трансформации — это рецепт, действие — поставить блюдо в духовку
```

---

### 20–50 | DataFrame API

#### Создание SparkSession

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# Локальный режим — использует все доступные ядра
spark = SparkSession.builder \
    .appName("Мой анализ") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Отключить лишние логи (для учебных целей)
spark.sparkContext.setLogLevel("ERROR")

print(spark.version)
```

#### Создание DataFrame

```python
# Из Python-списка
данные = [
    ("Германия", 4.07, 2.1),
    ("Франция",  2.78, 2.5),
    ("Италия",   2.10, 3.0),
]
схема = ["страна", "ввп", "инфляция"]
df = spark.createDataFrame(данные, schema=схема)

# Из CSV
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("transactions.csv")

# Из Parquet
df = spark.read.parquet("data.parquet")

# Явная схема — хорошая практика для больших данных
schema = StructType([
    StructField("id",         IntegerType(), nullable=False),
    StructField("сумма",      DoubleType(),  nullable=True),
    StructField("категория",  StringType(),  nullable=True),
])
df = spark.read.schema(schema).csv("transactions.csv", header=True)
```

#### Базовые операции: трансформации vs действия

```python
# ─── ТРАНСФОРМАЦИИ (ленивые, строят DAG) ───

# select — выбор столбцов
df.select("страна", "ввп")
df.select(F.col("ввп"), F.col("инфляция"))

# filter / where
df.filter(F.col("ввп") > 2.5)
df.where("ввп > 2.5")  # SQL-синтаксис

# withColumn — добавить/изменить столбец
df = df.withColumn("ввп_млрд", F.col("ввп") * 1000)
df = df.withColumn("категория", F.upper(F.col("категория")))

# drop
df = df.drop("временный_столбец")

# orderBy / sort
df.orderBy(F.col("ввп").desc())
df.sort("ввп", ascending=False)

# dropDuplicates
df.dropDuplicates(["клиент_id", "дата"])

# ─── ДЕЙСТВИЯ (запускают выполнение DAG) ───

df.show(5)              # напечатать первые 5 строк
df.show(5, truncate=False)  # не обрезать длинные строки
df.count()              # количество строк
df.collect()            # вернуть все строки как Python-список (осторожно!)
df.first()              # первая строка
df.take(10)             # первые 10 строк
df.printSchema()        # схема DataFrame
df.describe().show()    # описательная статистика
```

#### `withColumn` — преобразования

```python
from pyspark.sql import functions as F

df = spark.read.csv("sales.csv", header=True, inferSchema=True)

df = (df
    # Арифметика
    .withColumn("сумма_с_ндс", F.col("сумма") * 1.2)

    # Условие (аналог np.where)
    .withColumn("размер",
        F.when(F.col("сумма") > 1000, "крупная")
         .when(F.col("сумма") > 100, "средняя")
         .otherwise("малая")
    )

    # Строки
    .withColumn("категория", F.lower(F.trim(F.col("категория"))))

    # Дата
    .withColumn("дата", F.to_date(F.col("дата"), "yyyy-MM-dd"))
    .withColumn("год",  F.year(F.col("дата")))
    .withColumn("месяц", F.month(F.col("дата")))

    # Заполнить пропуски
    .fillna({"сумма": 0.0, "категория": "неизвестно"})
)

df.show(5)
```

---

### 50–75 | GroupBy, join и SQL-интерфейс

#### `groupBy` и агрегации

```python
from pyspark.sql import functions as F

# Одна группировка
df.groupBy("категория").agg(F.sum("сумма").alias("итого")).show()

# Несколько агрегаций
итоги = df.groupBy("регион", "категория").agg(
    F.sum("сумма").alias("выручка"),
    F.avg("сумма").alias("ср_чек"),
    F.count("*").alias("кол_сделок"),
    F.max("сумма").alias("макс_чек"),
    F.countDistinct("клиент_id").alias("уник_клиентов"),
)
итоги.orderBy(F.col("выручка").desc()).show()

# Оконные функции
from pyspark.sql.window import Window

окно = Window.partitionBy("регион").orderBy(F.col("сумма").desc())
df = df.withColumn("ранг_в_регионе", F.rank().over(окно))
df = df.withColumn("нарастающий_итог", F.sum("сумма").over(окно))
```

#### Join

```python
транзакции = spark.read.csv("transactions.csv", header=True, inferSchema=True)
клиенты    = spark.read.csv("clients.csv",      header=True, inferSchema=True)
продукты   = spark.read.csv("products.csv",     header=True, inferSchema=True)

# LEFT JOIN
результат = транзакции.join(клиенты, on="клиент_id", how="left")

# Разные имена ключей
результат = транзакции.join(
    клиенты,
    транзакции["клиент_id"] == клиенты["id"],
    how="inner"
)

# Broadcast join — для маленьких таблиц (избегает shuffle!)
from pyspark.sql.functions import broadcast
результат = транзакции.join(broadcast(продукты), on="продукт_id")
# Spark рассылает маленькую таблицу на все executors

# Несколько join
полный = (транзакции
    .join(broadcast(клиенты),  "клиент_id",  "left")
    .join(broadcast(продукты), "продукт_id", "left")
)
```

#### SQL-интерфейс

```python
# Зарегистрировать DataFrame как временную таблицу
транзакции.createOrReplaceTempView("транзакции")
клиенты.createOrReplaceTempView("клиенты")

# Обычный SQL!
результат = spark.sql("""
    SELECT
        к.сегмент,
        т.категория,
        SUM(т.сумма)   AS выручка,
        AVG(т.сумма)   AS ср_чек,
        COUNT(*)       AS кол_сделок
    FROM транзакции т
    LEFT JOIN клиенты к ON т.клиент_id = к.клиент_id
    WHERE т.сумма > 0
    GROUP BY к.сегмент, т.категория
    ORDER BY выручка DESC
""")
результат.show()

# Подзапросы, CTE, оконные функции — всё поддерживается
spark.sql("""
    WITH ежемесячные AS (
        SELECT
            DATE_TRUNC('month', дата) AS месяц,
            SUM(сумма) AS выручка
        FROM транзакции
        GROUP BY 1
    )
    SELECT
        месяц,
        выручка,
        LAG(выручка) OVER (ORDER BY месяц) AS пред_месяц,
        ROUND((выручка / LAG(выручка) OVER (ORDER BY месяц) - 1) * 100, 1) AS рост_pct
    FROM ежемесячные
""").show()
```

---

### 75–90 | Лабораторная работа

```python
# Та же задача, что в занятиях 7–9:
# фильтр → группировка → агрегация → join
# Теперь на PySpark

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import broadcast

spark = SparkSession.builder.appName("Lab10").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Чтение данных
транзакции = spark.read.csv("transactions.csv", header=True, inferSchema=True)
клиенты    = spark.read.csv("clients.csv",      header=True, inferSchema=True)

# Pipeline: фильтр → join → группировка → агрегация
результат = (
    транзакции
    # Очистка
    .withColumn("категория", F.lower(F.trim(F.col("категория"))))
    .withColumn("сумма", F.col("сумма").cast("double"))
    # Фильтр
    .filter(F.col("сумма") > 0)
    .filter(F.col("категория").isNotNull())
    # Join с клиентами
    .join(broadcast(клиенты), "клиент_id", "left")
    # Группировка
    .groupBy("сегмент", "категория")
    .agg(
        F.sum("сумма").alias("выручка"),
        F.avg("сумма").alias("ср_чек"),
        F.count("*").alias("кол_сделок"),
        F.countDistinct("клиент_id").alias("уник_клиентов"),
    )
    .orderBy(F.col("выручка").desc())
)

# Действие — запустить выполнение
результат.show(20, truncate=False)

# Сохранить результат
результат.write.mode("overwrite").parquet("output/итоги_по_сегментам")

# Остановить сессию
spark.stop()
```

---

## Проверка понимания

**5 вопросов:**

1. В чём разница между трансформацией и действием в Spark?
   > Трансформации (filter, select, withColumn) ленивы — строят граф операций (DAG), но ничего не выполняют. Действия (show, collect, count, write) запускают вычисление всего DAG. Это позволяет Spark оптимизировать весь план целиком.

2. Почему `df.collect()` опасен на большом кластере?
   > `collect()` переносит все данные из всех executors на driver-машину. Если данных терабайт — driver упадёт с OutOfMemoryError. Используйте `show(N)`, `take(N)` или записывайте результат в файл.

3. Что такое shuffle и почему он дорогой?
   > Shuffle — перераспределение данных между executors по сети (например, при groupBy или join). Данные сериализуются, передаются по сети и десериализуются на другом узле. Это самая медленная операция в Spark.

4. Зачем использовать `broadcast()` при join?
   > Если одна таблица маленькая (до нескольких сотен МБ), Spark может разослать её копию на все executors. Тогда join выполняется локально на каждом узле без shuffle — значительно быстрее.

5. Чем `spark.sql()` отличается от DataFrame API?
   > Результат одинаков — оба создают один и тот же план выполнения. `spark.sql()` удобен тем, кто хорошо знает SQL; DataFrame API легче генерировать программно и тестировать по частям.