# Глава 3 — Структуры данных Python

## Часть 1. `list`, `tuple`, `dict`, `set`

**Таблица сложности операций:**

| Структура | Доступ | Поиск | Вставка | Удаление | Примечания |
|---------|-----------------|---------------|-------------|-------------------|-----------------------------------------------------|
| `list`  | O(1) по индексу | O(n)          | O(1) append | O(n) произвольное | Упорядоченная, изменяемая                           |
| `tuple` | O(1) по индексу | O(n)          | —           | —                 | Неизменяемая, хешируемая                            |
| `dict`  | O(1) по ключу   | O(1) по ключу | O(1)        | O(1)              | Упорядоченная (3.7+), изменяемая                    |
| `set`   | —               | O(1)          | O(1)        | O(1)              | Неупорядоченная, без дубликатов, элементы хешируемы |

### 1.1 Почему `dict`/`set` быстрее `list` в поиске

Под капотом `dict` и `set` — это хеш-таблицы: значение находится по хешу ключа/элемента напрямую, без перебора. `list` требует линейного просмотра, если не известна позиция.

### 1.2 Требования к хешируемости

Ключом словаря или элементом множества может быть только **неизменяемый и хешируемый** объект.

### 1.3 Когда что использовать

- **`list`** — когда важен порядок и возможны дубликаты, нужен доступ по индексу.
- **`tuple`** — когда данные не должны меняться (координаты, RGB, строка таблицы), либо нужен хешируемый ключ.
- **`dict`** — когда нужен быстрый доступ "по имени/ключу", а не по позиции.
- **`set`** — когда важна только уникальность и быстрая проверка вхождения, порядок не важен.

## Часть 2. Изменяемость и идентичность

### 2.1 `is` vs `==`

`==` сравнивает **значения**, `is` сравнивает **идентичность объектов** (один и тот же объект в памяти).

**Частая ловушка:** сравнение с `None` всегда через `is`, а не `==`.

### 2.2 Изменяемые (mutable) и неизменяемые (immutable) типы

| Изменяемые            | Неизменяемые                                        |
|-----------------------|-----------------------------------------------------|
| `list`, `dict`, `set` | `tuple`, `str`, `int`, `float`, `bool`              |

### 2.3 Поверхностное и глубокое копирование

**Правило:** поверхностная копия копирует только верхний уровень контейнера — вложенные изменяемые объекты остаются общими (алиасинг). Глубокая копия рекурсивно копирует всё дерево объектов.

#### Исходный объект

```text
root
├── "a" ──► 1
└── "b" ──► list
            ├── 2
            └── 3
```

#### Поверхностная копия (`copy.copy()`)

```text
оригинал                 поверхностная копия
    │                            │
    ▼                            ▼
┌────────┐                  ┌────────┐
│  dict  │                  │  dict  │
└──┬──┬──┘                  └──┬──┬──┘
   │  │                         │  │
   │  └─────────────────────────┘  │
   │                                │
   ▼                                ▼
   1                         тот же самый list
                             ├── 2
                             └── 3
```

**Копируется только контейнер верхнего уровня.**
Вложенный изменяемый объект (`list`) **остаётся общим** для обеих копий (алиасинг).

### Глубокая копия (`copy.deepcopy()`)

```text
оригинал                     глубокая копия
    │                               │
    ▼                               ▼
┌────────┐                     ┌────────┐
│  dict  │                     │  dict  │
└──┬──┬──┘                     └──┬──┬──┘
   │  │                            │  │
   │  ▼                            │  ▼
   │ list A                        │ list B
   │ ├── 2                         │ ├── 2
   │ └── 3                         │ └── 3
   │
   ▼
   1
```

**Рекурсивно копируется всё дерево объектов.**
Каждый вложенный изменяемый объект получает **свою собственную копию**, поэтому изменения в одной структуре не влияют на другую.

=================================================================================================================================
## TODO: HERE!
=================================================================================================================================

### 2.4 Типичные ошибки с алиасингом

```python
# Ошибка: "размножение" вложенных списков через умножение
grid = [[0] * 3] * 3   # все три строки — ОДИН И ТОТ ЖЕ объект list!
grid[0][0] = 1
print(grid)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] — испортились все строки

# Правильно:
grid = [[0] * 3 for _ in range(3)]   # каждая строка — новый список
grid[0][0] = 1
print(grid)   # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

```python
# Передача изменяемого объекта в функцию — функция может изменить оригинал
def add_tax(order):
    order["total"] *= 1.2   # изменяет исходный словарь!
    return order

order = {"total": 100}
add_tax(order)
print(order["total"])   # 120.0 — оригинал изменился, это может быть неожиданно
```

---

## Часть 3. Модуль `collections` (45–65 мин)

Стандартная библиотека уже решила большинство "ручных" задач агрегации — не нужно писать `if key in dict` вручную.

### 3.1 `Counter` — подсчёт элементов

```python
from collections import Counter

words = ["еда", "транспорт", "еда", "развлечения", "еда", "транспорт"]

counts = Counter(words)
print(counts)                    # Counter({'еда': 3, 'транспорт': 2, 'развлечения': 1})
print(counts.most_common(2))     # [('еда', 3), ('транспорт', 2)]
print(counts["книги"])           # 0 — не бросает KeyError, в отличие от обычного dict!

# Арифметика счётчиков
c1 = Counter(["a", "b", "a"])
c2 = Counter(["a", "c"])
print(c1 + c2)   # Counter({'a': 3, 'b': 1, 'c': 1})
print(c1 - c2)   # Counter({'b': 1, 'a': 1})
```

### 3.2 `defaultdict` — словарь со значением по умолчанию

```python
from collections import defaultdict

# Без defaultdict — приходится проверять наличие ключа вручную
totals = {}
for category, amount in [("еда", 100), ("еда", 50), ("транспорт", 30)]:
    if category not in totals:
        totals[category] = 0
    totals[category] += amount

# С defaultdict — короче и без ветвлений
totals = defaultdict(int)
for category, amount in [("еда", 100), ("еда", 50), ("транспорт", 30)]:
    totals[category] += amount   # ключ создаётся автоматически со значением int() == 0

print(dict(totals))   # {'еда': 150, 'транспорт': 30}

# defaultdict(list) — группировка элементов
groups = defaultdict(list)
for category, order_id in [("еда", 1), ("еда", 2), ("транспорт", 3)]:
    groups[category].append(order_id)

print(dict(groups))   # {'еда': [1, 2], 'транспорт': [3]}
```

### 3.3 `namedtuple` — легковесные структуры с именованными полями

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)

print(p.x, p.y)      # 3 4 — обращение по имени, а не только по индексу
print(p[0], p[1])    # 3 4 — но и по индексу тоже работает
print(p)              # Point(x=3, y=4)

# Неизменяемость, как у обычного tuple
try:
    p.x = 10
except AttributeError as e:
    print(e)   # can't set attribute
```

> На следующем занятии разберём `@dataclass` — более современную альтернативу `namedtuple`, когда нужна изменяемость и методы.

### 3.4 `OrderedDict`

```python
from collections import OrderedDict

# С Python 3.7+ обычный dict уже сохраняет порядок вставки,
# но OrderedDict остаётся полезен для явного сравнения порядка
# и метода move_to_end()

od = OrderedDict()
od["a"] = 1
od["b"] = 2
od["c"] = 3

od.move_to_end("a")
print(od)   # OrderedDict([('b', 2), ('c', 3), ('a', 1)])

# Частый кейс: LRU-кеш вручную
od.move_to_end("b", last=False)   # переместить в начало
```

---

## Часть 4. Comprehensions и вложенные структуры (65–85 мин)

### 4.1 List, dict и set comprehensions

```python
squares = [x ** 2 for x in range(10)]

square_map = {x: x ** 2 for x in range(10)}

unique_lengths = {len(word) for word in ["кот", "собака", "кит", "слон"]}

# С условием
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]

# Вложенный comprehension — "выпрямление" матрицы
matrix = [[1, 2, 3], [4, 5, 6]]
flat = [x for row in matrix for x in row]   # [1, 2, 3, 4, 5, 6]
```

### 4.2 Производительность: comprehension vs цикл vs `map`/`filter`

```python
import timeit

n = 1_000_000

t_loop = timeit.timeit(
    "result = []\nfor x in range(n): result.append(x * 2)",
    globals={"n": n}, number=5
)

t_comp = timeit.timeit(
    "[x * 2 for x in range(n)]",
    globals={"n": n}, number=5
)

t_map = timeit.timeit(
    "list(map(lambda x: x * 2, range(n)))",
    globals={"n": n}, number=5
)

print(f"цикл: {t_loop:.3f}, comprehension: {t_comp:.3f}, map: {t_map:.3f}")
# comprehension обычно быстрее ручного цикла за счёт оптимизации на уровне байткода
```

**Практическое правило:** comprehension предпочтителен для простых преобразований в одну строку; если логика требует нескольких условий/веток — читаемость важнее, лучше обычный цикл или именованная функция.

### 4.3 Обработка JSON-подобных данных

```python
orders = [
    {"id": 1, "customer": {"name": "Аня", "city": "Москва"}, "items": [{"sku": "A1", "qty": 2}]},
    {"id": 2, "customer": {"name": "Борис", "city": "Казань"}, "items": [{"sku": "B2", "qty": 1}, {"sku": "A1", "qty": 3}]},
]

# Извлечь все города
cities = {order["customer"]["city"] for order in orders}

# Посчитать общее количество по SKU — вложенный обход через collections
from collections import defaultdict

sku_totals = defaultdict(int)
for order in orders:
    for item in order["items"]:
        sku_totals[item["sku"]] += item["qty"]

print(dict(sku_totals))   # {'A1': 5, 'B2': 1}

# Безопасное извлечение при отсутствующих полях — .get() вместо []
discount = order.get("discount", 0)   # не упадёт, если ключа нет
```

### 4.4 Рекурсивный обход вложенных структур

```python
def flatten(data):
    """Рекурсивно 'выпрямляет' произвольно вложенные списки."""
    result = []
    for item in data:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

nested = [1, [2, 3, [4, 5], 6], [7, [8, [9]]]]
print(flatten(nested))   # [1, 2, 3, 4, 5, 6, 7, 8, 9]

def find_all_keys(data, target_key, path=""):
    """Рекурсивно ищет все вхождения ключа в произвольно вложенном dict/list."""
    found = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if key == target_key:
                found.append((current_path, value))
            found.extend(find_all_keys(value, target_key, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found.extend(find_all_keys(item, target_key, f"{path}[{i}]"))
    return found

print(find_all_keys(orders, "city"))
# [('[0].customer.city', 'Москва'), ('[1].customer.city', 'Казань')]
```

---

## Часть 5. Демонстрация: "грязные" данные о заказах

Дан список словарей с неполными, неоднородными данными:

```python
raw_orders = [
    {"category": "еда", "amount": 450.0},
    {"category": "транспорт", "amount": 120.0},
    {"category": "еда"},                              # отсутствует amount
    {"amount": 900.0},                                 # отсутствует category
    {"category": "еда", "amount": 300.0},
    {"category": "транспорт", "amount": 80.0},
    {"category": "развлечения", "amount": None},       # amount = None
]
```

**Ручной способ (то, как писали бы без `collections`):**

```python
totals = {}
counts = {}
for order in raw_orders:
    category = order.get("category")
    amount = order.get("amount")
    if category is None or amount is None:
        continue
    if category not in totals:
        totals[category] = 0.0
        counts[category] = 0
    totals[category] += amount
    counts[category] += 1

print(totals)
print(counts)
```

**С `Counter`/`defaultdict`:**

```python
from collections import defaultdict, Counter

totals = defaultdict(float)
counts = Counter()

for order in raw_orders:
    category = order.get("category")
    amount = order.get("amount")
    if category is None or amount is None:
        continue
    totals[category] += amount
    counts[category] += 1

print(dict(totals))   # {'еда': 750.0, 'транспорт': 200.0}
print(counts)          # Counter({'еда': 2, 'транспорт': 2})
```

**Обсуждение на экране:** второй вариант короче, без ручной инициализации ключей, `Counter` сразу даёт `most_common()` для рейтинга категорий. Это именно тот код, который приходится читать/писать в реальных пайплайнах до того, как задача переезжает на `pandas.groupby`.

---

## Введение в домашнее задание (85–90 мин)

**Постановка задачи:** дан файл с "грязными" данными о заказах (вложенные словари, отсутствующие поля, дубликаты). Нужно:

- построить агрегацию по категориям и по клиентам с помощью `Counter`/`defaultdict`;
- реализовать функцию глубокой очистки вложенной структуры от `None`-значений без использования `copy.deepcopy` напрямую — с явным пониманием, где создаётся новый объект, а где остаётся алиасинг;
- написать рекурсивную функцию поиска по вложенной структуре произвольной глубины;
- сравнить время выполнения агрегации через ручной цикл и через `collections`, зафиксировать результат.

Детальное описание, критерии оценки и стартовые данные — в файле задания в LMS.

---

## Материалы и ресурсы

- [Документация модуля collections](https://docs.python.org/3/library/collections.html)
- [Модель данных Python — хешируемость](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Модуль copy](https://docs.python.org/3/library/copy.html)
- [Time complexity — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- Рекомендуемое чтение: *Fluent Python*, главы 2–3 (списки, словари, множества)