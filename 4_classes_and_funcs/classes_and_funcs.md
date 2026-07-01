# Занятие 4 — Продвинутый Python: синтаксический сахар, типизация, парадигмы программирования

**Цель занятия:** дать словарный запас, который повсеместно встречается во "взрослом" коде анализа данных, и показать, как один и тот же результат получается в разных парадигмах — чтобы студенты осознанно выбирали подход под задачу.

---

## Часть 1. Синтаксический сахар (0–25 мин)

Синтаксический сахар — это конструкции языка, которые не добавляют новых возможностей, но делают код короче и выразительнее. Задача этого блока — научиться *читать* такой код, даже если сами вы пока пишете проще.

### 1.1 Walrus-оператор `:=` (Python 3.8+)

Позволяет присвоить значение переменной прямо внутри выражения.

```python
# Без walrus
data = get_data()
if data:
    process(data)

# С walrus — то же самое, но без дублирования вызова
if (data := get_data()):
    process(data)

# Классика: фильтрация с побочным сохранением результата
results = [y for x in values if (y := expensive_func(x)) is not None]
```

**Когда полезно:** циклы `while`, list comprehension с промежуточным вычислением, чтобы не вызывать функцию дважды.

### 1.2 Тернарный оператор

```python
status = "активен" if user.is_active else "неактивен"

# Вложенный (использовать осторожно — читаемость страдает быстро)
grade = "A" if score >= 90 else "B" if score >= 75 else "C"
```

### 1.3 Распаковка (unpacking)

```python
a, b, c = 1, 2, 3

first, *rest = [1, 2, 3, 4, 5]        # first=1, rest=[2,3,4,5]
*init, last = [1, 2, 3, 4, 5]         # init=[1,2,3,4], last=5
first, *middle, last = range(10)

# Распаковка в函数-вызовах
def total(a, b, c):
    return a + b + c

args = (1, 2, 3)
total(*args)

# Слияние словарей через **
defaults = {"debug": False, "timeout": 30}
config = {**defaults, "timeout": 60}   # переопределяем один ключ
```

### 1.4 `*args` и `**kwargs`

```python
def log_call(*args, **kwargs):
    print(f"Позиционные: {args}, именованные: {kwargs}")

log_call(1, 2, name="Иван", role="analyst")
# Позиционные: (1, 2), именованные: {'name': 'Иван', 'role': 'analyst'}
```

Используется повсеместно в декораторах, обёртках API, ORM-моделях — везде, где нужно "прозрачно" прокинуть произвольные аргументы дальше.

### 1.5 `zip` и `enumerate`

```python
names = ["Аня", "Борис", "Вера"]
scores = [85, 92, 78]

for i, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"{i}. {name}: {score}")

# zip для транспонирования матрицы
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = list(zip(*matrix))   # [(1, 4), (2, 5), (3, 6)]
```

### 1.6 Продвинутые f-strings

```python
value = 1234567.891
print(f"{value:,.2f}")        # 1,234,567.89
print(f"{value:.2e}")         # 1.23e+06

name = "Мария"
print(f"{name=}")             # name='Мария'  — отладочный вывод, Python 3.8+

pi = 3.14159
print(f"{pi:>10.2f}")         # выравнивание по правому краю, ширина 10
```

### 1.7 Декораторы

Декоратор — это функция, которая принимает функцию и возвращает новую функцию (обычно — обёртку с дополнительным поведением).

```python
import functools
import time

def timer(func):
    @functools.wraps(func)   # сохраняет имя и докстринг оригинальной функции
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} выполнилась за {elapsed:.4f} сек")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

slow_sum(10_000_000)
```

**Как это работает "под капотом":**

```python
@timer
def foo(): ...

# эквивалентно
def foo(): ...
foo = timer(foo)
```

Декоратор с параметрами — это функция, возвращающая декоратор:

```python
def retry(times=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Попытка {attempt + 1} не удалась: {e}")
            raise RuntimeError("Все попытки исчерпаны")
        return wrapper
    return decorator

@retry(times=5)
def fetch_from_api(): ...
```

---

## Часть 2. Типизация (25–45 мин)

Python — язык с динамической типизацией, но модуль `typing` даёт статические подсказки типов, которые проверяются внешними инструментами (не интерпретатором!).

### 2.1 Базовые аннотации

```python
def greet(name: str, age: int = 18) -> str:
    return f"{name}, {age} лет"

numbers: list[int] = [1, 2, 3]
mapping: dict[str, float] = {"eur": 1.1, "usd": 1.0}
```

> В Python 3.9+ можно писать `list[int]`, `dict[str, int]` напрямую, без импорта `List`/`Dict` из `typing`.

### 2.2 `Optional`, `Union` и `|`

```python
from typing import Optional, Union

def find_user(user_id: int) -> Optional[dict]:
    # Optional[dict] == Union[dict, None]
    ...

def parse(value: Union[str, int]) -> float:
    ...

# Python 3.10+: короткий синтаксис
def parse_new(value: str | int) -> float:
    ...

def find_user_new(user_id: int) -> dict | None:
    ...
```

### 2.3 `Literal`

Ограничивает значение конкретным набором вариантов — полезно для флагов и режимов.

```python
from typing import Literal

def set_mode(mode: Literal["train", "eval", "predict"]) -> None:
    ...

set_mode("train")     # ок
set_mode("debug")     # mypy подсветит ошибку
```

### 2.4 `@dataclass` — замена "словарей с данными"

Частая ошибка в аналитическом коде — таскать данные в "голых" словарях (`{"name": ..., "value": ...}`), где легко опечататься в ключе и получить `KeyError` в рантайме. `dataclass` решает это через явную структуру.

```python
from dataclasses import dataclass, field

@dataclass
class Transaction:
    id: int
    category: str
    amount: float
    tags: list[str] = field(default_factory=list)

t = Transaction(id=1, category="еда", amount=450.0)
print(t)                     # автоматический __repr__
print(t.amount)               # обращение через атрибут, не через ["amount"]
```

`@dataclass` бесплатно генерирует `__init__`, `__repr__`, `__eq__`. Сравните со словарём:

```python
# Словарь: опечатка в ключе — ошибка только в рантайме
tx = {"categoty": "еда", "amount": 450.0}   # опечатка не будет замечена статически

# Dataclass: опечатка в поле — mypy/IDE подсветят сразу
tx = Transaction(categoty="еда", amount=450.0)   # ошибка обнаружена до запуска
```

### 2.5 Базовые `Protocol` и `Generic`

`Protocol` — "утиная типизация" со статической проверкой: объект подходит под тип, если у него есть нужные методы, без явного наследования.

```python
from typing import Protocol

class Reporter(Protocol):
    def report(self) -> str: ...

def print_report(obj: Reporter) -> None:
    print(obj.report())

# Любой класс с методом report() подходит — не нужно наследоваться от Reporter
class SalesSummary:
    def report(self) -> str:
        return "Отчёт по продажам"

print_report(SalesSummary())   # ок для mypy
```

`Generic` — типизированные контейнеры/классы, параметризуемые типом:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

int_stack: Stack[int] = Stack()
int_stack.push(5)
```

### 2.6 Зачем `mypy` в команде

- Типы — это **исполняемая документация**: не нужно лезть в реализацию функции, чтобы понять, что она принимает и возвращает.
- Статический анализатор (`mypy`, `pyright`) ловит ошибки типов **до** запуска кода — особенно ценно в пайплайнах данных, где ошибка вылезает через час обработки.
- Упрощает ревью кода и рефакторинг больших кодовых баз.
- **Важно проговорить:** аннотации типов в Python — это подсказки, интерпретатор их не проверяет. Проверка — задача отдельного инструмента (`mypy`), который обычно встраивают в CI.

---

## Часть 3. Парадигмы программирования (45–70 мин)

Одну и ту же задачу можно решить разными "стилями мышления". Разберём три классических подхода на одном примере.

**Задача:** посчитать суммарные продажи по категориям из списка транзакций.

```python
transactions = [
    {"category": "еда", "amount": 450.0},
    {"category": "транспорт", "amount": 120.0},
    {"category": "еда", "amount": 300.0},
    {"category": "развлечения", "amount": 900.0},
    {"category": "транспорт", "amount": 80.0},
]
```

### 3.1 Процедурный стиль

```python
totals = {}
for tx in transactions:
    category = tx["category"]
    amount = tx["amount"]
    if category not in totals:
        totals[category] = 0.0
    totals[category] += amount

print(totals)
```

Прямолинейно, легко читается новичком, но: изменяемое состояние (`totals`) собирается вручную, легко забыть проверку `if category not in totals`.

### 3.2 Функциональный стиль

```python
from functools import reduce
from collections import defaultdict

# Вариант через reduce
def accumulate(acc: dict, tx: dict) -> dict:
    acc[tx["category"]] = acc.get(tx["category"], 0.0) + tx["amount"]
    return acc

totals = reduce(accumulate, transactions, {})

# Более "питонический" функциональный вариант — через defaultdict + comprehension
totals = defaultdict(float)
for category, amount in ((tx["category"], tx["amount"]) for tx in transactions):
    totals[category] += amount
```

Акцент на *чистых функциях* (без побочных эффектов) и неизменяемости данных на входе. `map`/`filter` пригодились бы, например, для предварительной фильтрации:

```python
big_transactions = list(filter(lambda tx: tx["amount"] > 200, transactions))
amounts = list(map(lambda tx: tx["amount"], transactions))
```

### 3.3 Объектно-ориентированный стиль

```python
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Transaction:
    category: str
    amount: float

class SalesAggregator:
    def __init__(self) -> None:
        self._totals: dict[str, float] = defaultdict(float)

    def add(self, transaction: Transaction) -> None:
        self._totals[transaction.category] += transaction.amount

    def as_dict(self) -> dict[str, float]:
        return dict(self._totals)

    def __repr__(self) -> str:
        return f"SalesAggregator({self.as_dict()})"

aggregator = SalesAggregator()
for tx in transactions:
    aggregator.add(Transaction(**tx))

print(aggregator)
```

Здесь состояние инкапсулировано внутри объекта, а не "болтается" в глобальной переменной. Легко расширить: добавить метод `top_category()`, `reset()`, логирование и т.д. без изменения внешнего интерфейса.

### 3.4 ООП: наследование vs композиция

```python
# Наследование — "является" (is-a)
class BaseAggregator:
    def __init__(self):
        self._totals = defaultdict(float)

    def add(self, category: str, amount: float) -> None:
        self._totals[category] += amount

class WeightedAggregator(BaseAggregator):
    def add(self, category: str, amount: float, weight: float = 1.0) -> None:
        self._totals[category] += amount * weight

# Композиция — "содержит" (has-a), обычно гибче
class ReportBuilder:
    def __init__(self, aggregator: BaseAggregator) -> None:
        self._aggregator = aggregator   # используем через композицию, не наследуемся

    def build(self) -> str:
        return "\n".join(f"{k}: {v:.2f}" for k, v in self._aggregator._totals.items())
```

**Практическое правило:** "composition over inheritance" — наследование создаёт жёсткую связь между классами и легко приводит к хрупким иерархиям при росте требований; композиция даёт гибкость и упрощает тестирование.

### 3.5 Dunder-методы

```python
class Money:
    def __init__(self, amount: float, currency: str = "RUB"):
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать разные валюты")
        return Money(self.amount + other.amount, self.currency)

a = Money(100)
b = Money(50)
print(a + b)          # Money(150, 'RUB')
print(a == Money(100))  # True
```

### 3.6 Обсуждение: что выбрать?

| Критерий | Процедурный | Функциональный | ООП |
|---|---|---|---|
| Порог входа | Низкий | Средний | Средний-высокий |
| Тестируемость | Средняя | Высокая (чистые функции) | Высокая (изоляция состояния) |
| Расширяемость при росте требований | Низкая | Средняя | Высокая |
| Типичное применение | Скрипты, разовые расчёты | Пайплайны трансформации данных | Долгоживущие системы, домены с состоянием |
| Риски | "Спагетти"-код при росте | Плохая читаемость при избыточной вложенности | Излишняя абстракция для простых задач |

**Ключевая мысль для студентов:** парадигма — это инструмент, а не религия. В одном модуле нормально сочетать функциональные трансформации данных (`pandas`, comprehensions) с объектной инкапсуляцией бизнес-логики.

---

## Часть 4. Исключения и контекстные менеджеры (70–85 мин)

### 4.1 `try / except / else / finally`

```python
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Файл {path} не найден, используем значения по умолчанию")
        return {}
    except PermissionError as e:
        print(f"Нет доступа: {e}")
        raise
    else:
        # выполняется, только если исключений не было
        print("Файл успешно прочитан")
        return parse(data)
    finally:
        # выполняется всегда — используется для очистки ресурсов
        print("Попытка чтения конфигурации завершена")
```

### 4.2 Кастомные исключения

```python
class DataValidationError(Exception):
    """Базовое исключение для ошибок валидации данных."""

class MissingColumnError(DataValidationError):
    def __init__(self, column: str):
        self.column = column
        super().__init__(f"Отсутствует обязательная колонка: {column}")

def validate(df_columns: set[str]) -> None:
    required = {"category", "amount"}
    missing = required - df_columns
    if missing:
        raise MissingColumnError(missing.pop())

try:
    validate({"category"})
except MissingColumnError as e:
    print(f"Ошибка валидации: {e}, колонка: {e.column}")
```

Собственная иерархия исключений позволяет вызывающему коду ловить как конкретную ошибку, так и целую категорию (`except DataValidationError`).

### 4.3 `with` и протокол контекстного менеджера

```python
with open("data.csv") as f:
    content = f.read()
# файл гарантированно закрыт, даже если внутри блока было исключение
```

### 4.4 Собственный контекстный менеджер — через класс

```python
import time

class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self._start
        print(f"Блок выполнился за {elapsed:.4f} сек")
        return False   # False = не подавлять исключение, если оно было

with Timer():
    total = sum(range(10_000_000))
```

### 4.5 Собственный контекстный менеджер — через `contextlib.contextmanager`

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Блок выполнился за {elapsed:.4f} сек")

with timer():
    total = sum(range(10_000_000))
```

**Сравнение подходов:** класс — явный и удобен, когда нужно хранить состояние между `__enter__`/`__exit__` или переиспользовать логику через наследование. `contextmanager`-декоратор — короче для простых одноразовых случаев.

---

## Часть 5. Итоговая демонстрация (в рамках занятия)

Разбираем на экране все три реализации задачи "суммарные продажи по категориям" (процедурная / функциональная / ООП, см. Часть 3) бок о бок и обсуждаем:

1. Что произойдёт с каждым подходом, если требования изменятся: нужно добавить фильтрацию по дате, поддержку нескольких валют, кеширование результата?
2. Какой вариант проще покрыть unit-тестами?
3. Какой вариант проще прочитать человеку, который видит код впервые?

---

## Введение в домашнее задание (85–90 мин)

**Постановка задачи:** реализовать модуль обработки транзакций, который:

- использует `@dataclass` для представления транзакции с типизированными полями (`typing`, `Literal` для категории или статуса);
- предоставляет функциональную и объектно-ориентированную реализацию агрегации (на выбор студента — какую делать основной, какую альтернативной);
- обрабатывает некорректные данные через кастomные исключения;
- использует хотя бы один собственный контекстный менеджер (например, для логирования времени обработки или безопасной записи результата в файл);
- проходит проверку `mypy` без ошибок.

Детальное описание, критерии оценки и шаблон репозитория — в файле задания в LMS.

---

## Материалы и ресурсы

- [Документация модуля `typing`](https://docs.python.org/3/library/typing.html)
- [PEP 526 — Syntax for Variable Annotations](https://peps.python.org/pep-0526/)
- [PEP 572 — Assignment Expressions (walrus)](https://peps.python.org/pep-0572/)
- [Документация `dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [Документация `functools`](https://docs.python.org/3/library/functools.html)
- [Документация `contextlib`](https://docs.python.org/3/library/contextlib.html)
- [mypy — официальная документация](https://mypy.readthedocs.io/)
- Рекомендуемое чтение: *Fluent Python* (Luciano Ramalho), главы 7–9 (функции как объекты, декораторы, замыкания), 11 (протоколы и ABC)
- Рекомендуемое чтение: *Python Distilled* (David Beazley), глава 7 (классы и ООП)