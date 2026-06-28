# Занятие 8. Pandas II: группировка, объединение, время, EDA
**Блок 6 — Библиотеки | Продолжительность: 90 минут | Уровень: Средний**

---

## Цели обучения

К концу занятия студенты смогут:
1. Агрегировать данные с помощью `groupby` и сводных таблиц.
2. Объединять DataFrame через `merge`/`join`/`concat`.
3. Работать с пропусками и временными рядами.
4. Проводить полный мини-EDA: описательная статистика, выбросы, корреляции.

---

## Поминутный план

### 0–25 | GroupBy и сводные таблицы

#### Базовый `groupby`

```python
import pandas as pd
import numpy as np

df = pd.read_csv("sales.csv")
# Столбцы: дата, регион, категория, продавец, сумма, количество

# Одна группировка
по_региону = df.groupby("регион")["сумма"].sum()
print(по_региону)

# Несколько агрегаций
stats = df.groupby("регион")["сумма"].agg(["mean", "sum", "count", "std"])
print(stats)

# Группировка по нескольким столбцам
по_рег_кат = df.groupby(["регион", "категория"])["сумма"].sum()
print(по_рег_кат)
print(по_рег_кат.unstack())  # превратить в "широкую" таблицу
```

#### Именованные агрегации — явный и читаемый синтаксис

```python
# Синтаксис: новое_имя=("столбец", "функция")
итоги = df.groupby("регион").agg(
    выручка=("сумма", "sum"),
    ср_чек=("сумма", "mean"),
    кол_сделок=("сумма", "count"),
    макс_чек=("сумма", "max"),
    уник_продавцов=("продавец", "nunique"),
)
print(итоги)

# Пользовательская функция в agg
итоги = df.groupby("регион").agg(
    iqr=("сумма", lambda x: x.quantile(0.75) - x.quantile(0.25)),
    топ_квартиль=("сумма", lambda x: x[x > x.quantile(0.75)].mean()),
)
```

#### `transform` — вернуть результат той же формы

```python
# Добавить средний чек по региону как новый столбец (не сворачивая строки)
df["ср_чек_региона"] = df.groupby("регион")["сумма"].transform("mean")

# Доля от суммы региона
df["доля_от_региона"] = df["сумма"] / df.groupby("регион")["сумма"].transform("sum")

# Z-score внутри каждой группы
df["z_score"] = df.groupby("регион")["сумма"].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

#### `pivot_table` и `melt`

```python
# pivot_table — сводная таблица (как в Excel)
сводная = pd.pivot_table(
    df,
    values="сумма",
    index="регион",
    columns="категория",
    aggfunc="sum",
    fill_value=0,
    margins=True,      # строка/столбец итогов
    margins_name="Итого",
)
print(сводная)

# melt — обратная операция: "широкая" таблица → "длинная"
широкая = pd.DataFrame({
    "регион":       ["Север", "Юг", "Запад"],
    "Еда":          [100, 200, 150],
    "Электроника":  [300, 250, 400],
    "Транспорт":    [50, 80, 60],
})

длинная = широкая.melt(
    id_vars=["регион"],
    var_name="категория",
    value_name="выручка",
)
print(длинная)
```

---

### 25–45 | Объединение данных

#### `pd.concat` — склеивание

```python
# По строкам (вертикально) — одинаковые столбцы
q1 = pd.read_csv("q1_sales.csv")
q2 = pd.read_csv("q2_sales.csv")
q3 = pd.read_csv("q3_sales.csv")

год = pd.concat([q1, q2, q3], ignore_index=True)

# По столбцам (горизонтально)
df_wide = pd.concat([df_features, df_targets], axis=1)
```

#### `merge` — аналог SQL JOIN

```python
транзакции = pd.DataFrame({
    "id":         [1, 2, 3, 4, 5],
    "клиент_id":  [101, 102, 101, 103, 102],
    "сумма":      [250, 1200, 89, 500, 300],
})

клиенты = pd.DataFrame({
    "клиент_id": [101, 102, 103, 104],
    "имя":       ["Иванов", "Петрова", "Сидоров", "Козлова"],
    "сегмент":   ["VIP", "Стандарт", "VIP", "Стандарт"],
})

# INNER JOIN — только совпадающие записи
df = pd.merge(транзакции, клиенты, on="клиент_id", how="inner")

# LEFT JOIN — все транзакции, даже без клиента
df = pd.merge(транзакции, клиенты, on="клиент_id", how="left")

# Разные имена ключевых столбцов
df = pd.merge(транзакции, клиенты,
              left_on="клиент_id", right_on="id_клиента")

# Проверка качества объединения — не забывать!
df = pd.merge(транзакции, клиенты, on="клиент_id",
              how="left", validate="many_to_one")
# validate raises: если в "один" есть дубликаты — это проблема данных

# Проверить пропуски после LEFT JOIN
print(df[df["имя"].isna()])  # транзакции без клиента
```

#### `join` — упрощённый merge по индексу

```python
df1 = pd.DataFrame({"выручка": [100, 200]}, index=["A", "B"])
df2 = pd.DataFrame({"расходы": [80, 150]}, index=["A", "B"])

результат = df1.join(df2)
print(результат)
```

---

### 45–65 | Пропуски и время

#### Работа с пропусками

```python
df = pd.read_csv("sales.csv")

# Обнаружение пропусков
print(df.isna().sum())          # сколько пропусков в каждом столбце
print(df.isna().mean() * 100)   # доля пропусков в %

# Удаление строк с пропусками
df_clean = df.dropna()                          # удалить все строки с хоть одним NaN
df_clean = df.dropna(subset=["сумма", "дата"]) # только если NaN в ключевых столбцах
df_clean = df.dropna(thresh=5)                 # оставить строки с >= 5 непустыми значениями

# Заполнение пропусков
df["сумма"] = df["сумма"].fillna(df["сумма"].median())   # медиана
df["регион"] = df["регион"].fillna("Неизвестно")          # константа
df["сумма"] = df["сумма"].fillna(method="ffill")          # предыдущее значение
df["сумма"] = df["сумма"].fillna(method="bfill")          # следующее значение

# Интерполяция (для временных рядов)
df["цена"] = df["цена"].interpolate(method="linear")
```

#### Категориальный dtype

```python
# Экономит память при небольшом числе уникальных значений
print(df["категория"].dtype)         # object (строки)
df["категория"] = df["категория"].astype("category")
print(df["категория"].dtype)         # category

print(df["категория"].cat.categories)    # ['еда', 'транспорт', 'электроника']
print(df["категория"].cat.codes)         # числовые коды

# Экономия памяти
print(df["категория"].nbytes)            # до
df["категория"] = df["категория"].astype("category")
print(df["категория"].nbytes)            # после (значительно меньше)
```

#### Работа с датами и временем

```python
df["дата"] = pd.to_datetime(df["дата"])

# Аксессор .dt — извлечение компонентов
df["год"]       = df["дата"].dt.year
df["месяц"]     = df["дата"].dt.month
df["день_нед"]  = df["дата"].dt.day_name()
df["квартал"]   = df["дата"].dt.quarter
df["нед_года"]  = df["дата"].dt.isocalendar().week

# Арифметика с датами
df["дней_с_начала"] = (df["дата"] - df["дата"].min()).dt.days

# Ресемплинг временных рядов
df_ts = df.set_index("дата")

# Агрегация по периодам
месячные = df_ts["сумма"].resample("M").sum()    # ежемесячно
квартальные = df_ts["сумма"].resample("Q").mean() # поквартально
недельные = df_ts["сумма"].resample("W").agg(["sum", "count"])

# Скользящее среднее
df_ts["скол_ср_7д"] = df_ts["сумма"].rolling(window=7).mean()
df_ts["скол_ср_30д"] = df_ts["сумма"].rolling(window=30).mean()
```

---

### 65–90 | EDA на практике

#### `.describe()` и первичный осмотр

```python
df = pd.read_csv("sales.csv", parse_dates=["дата"])

# Числовые столбцы
print(df.describe())
# count, mean, std, min, 25%, 50%, 75%, max

# Категориальные столбцы
print(df.describe(include="object"))
# count, unique, top (самое частое), freq

# Все столбцы
print(df.describe(include="all"))
```

#### `value_counts` и распределения

```python
# Частотное распределение
print(df["категория"].value_counts())
print(df["категория"].value_counts(normalize=True) * 100)  # в %

# Разбивка по диапазонам
df["размер_чека"] = pd.cut(
    df["сумма"],
    bins=[0, 100, 500, 1000, float("inf")],
    labels=["малый", "средний", "крупный", "очень крупный"]
)
print(df["размер_чека"].value_counts())
```

#### Матрица корреляций

```python
# Корреляции числовых столбцов
corr = df[["сумма", "количество", "маржа"]].corr()
print(corr)

# Тепловая карта
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Матрица корреляций")
plt.tight_layout()
plt.savefig("corr_heatmap.png", dpi=150)
plt.show()
```

#### Обнаружение выбросов

```python
# Метод IQR
Q1 = df["сумма"].quantile(0.25)
Q3 = df["сумма"].quantile(0.75)
IQR = Q3 - Q1

нижняя_граница = Q1 - 1.5 * IQR
верхняя_граница = Q3 + 1.5 * IQR

выбросы = df[(df["сумма"] < нижняя_граница) | (df["сумма"] > верхняя_граница)]
print(f"Выбросов: {len(выбросы)} ({len(выбросы)/len(df)*100:.1f}%)")

# Метод Z-score
df["z_score"] = (df["сумма"] - df["сумма"].mean()) / df["сумма"].std()
выбросы_z = df[df["z_score"].abs() > 3]
print(f"Выбросов по Z-score: {len(выбросы_z)}")

# Визуализация
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
df["сумма"].hist(bins=50, ax=axes[0])
axes[0].set_title("Распределение суммы")
df.boxplot(column="сумма", by="категория", ax=axes[1])
axes[1].set_title("Boxplot по категориям")
plt.tight_layout()
plt.savefig("outliers.png", dpi=150)
plt.show()
```

---

## Живая демонстрация: полный мини-EDA датасета продаж

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Загрузка ---
df = pd.read_csv("sales.csv", parse_dates=["дата"])
print(f"Форма датасета: {df.shape}")
print(df.dtypes)
print(df.head())

# --- 1. Описательная статистика ---
print("\n=== Числовые переменные ===")
print(df.describe())
print("\n=== Категориальные переменные ===")
print(df.describe(include="object"))

# --- 2. Пропуски ---
пропуски = df.isna().mean() * 100
print("\n=== Пропуски (%) ===")
print(пропуски[пропуски > 0])

# --- 3. Распределения ---
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
df["сумма"].hist(bins=50, ax=axes[0, 0])
axes[0, 0].set_title("Распределение суммы")

df["категория"].value_counts().plot(kind="bar", ax=axes[0, 1])
axes[0, 1].set_title("Количество по категориям")

df.groupby("регион")["сумма"].sum().plot(kind="bar", ax=axes[1, 0])
axes[1, 0].set_title("Выручка по регионам")

# Временной ряд
df.set_index("дата")["сумма"].resample("W").sum().plot(ax=axes[1, 1])
axes[1, 1].set_title("Еженедельная выручка")

plt.tight_layout()
plt.savefig("eda_distributions.png", dpi=150)
plt.show()

# --- 4. Корреляции ---
corr = df[["сумма", "количество", "маржа"]].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Матрица корреляций")
plt.tight_layout()
plt.savefig("eda_corr.png", dpi=150)
plt.show()

# --- 5. Выбросы (IQR) ---
Q1, Q3 = df["сумма"].quantile([0.25, 0.75])
IQR = Q3 - Q1
выбросы = df[(df["сумма"] < Q1 - 1.5 * IQR) | (df["сумма"] > Q3 + 1.5 * IQR)]
print(f"\nВыбросов: {len(выбросы)}")

# --- 6. Гипотезы для дальнейшего анализа ---
print("\n=== Гипотезы ===")
print("1. VIP-клиенты генерируют непропорционально высокую выручку.")
print("2. Выбросы сосредоточены в категории 'Электроника'.")
print("3. Выручка демонстрирует недельную сезонность.")
```

---

## Проверка понимания

**5 вопросов:**

1. Чем `groupby().agg()` отличается от `groupby().transform()`?
   > `agg()` сворачивает группы в одну строку на группу. `transform()` возвращает Series той же формы, что и исходная — удобно добавлять агрегат как новый столбец без merge.

2. Какой тип JOIN нужен, чтобы оставить все строки из левой таблицы, даже если в правой нет совпадения?
   > LEFT JOIN: `pd.merge(левая, правая, on="ключ", how="left")`.

3. Зачем использовать `validate=` в `pd.merge()`?
   > Чтобы явно проверить кардинальность связи. Если ожидается "many_to_one", но в правой таблице есть дубликаты ключа, merge молча создаст лишние строки — `validate` вызовет ошибку.

4. Почему `resample("M")` требует, чтобы индекс был DatetimeIndex?
   > Ресемплинг — операция над временной осью. pandas должен знать, к какому периоду относится каждая строка; без DatetimeIndex он не может группировать по временным интервалам.

5. В чём разница между IQR и Z-score при поиске выбросов?
   > IQR основан на квантилях и устойчив к самим выбросам — хорош при скошенных распределениях. Z-score основан на среднем и стандартном отклонении, которые сами чувствительны к выбросам — лучше подходит для нормально распределённых данных.