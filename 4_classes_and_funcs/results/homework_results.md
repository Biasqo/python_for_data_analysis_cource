# Ответы. Домашнее задание — Глава 4

---

## Упражнение 1. Walrus-оператор

```python
def parse_error_code(s: str) -> int | None:
    if s.startswith("error:"):
        return int(s.split(":")[1].strip())
    return None

logs = ["error: 12", "ok", "error: 45", "info", "error: 7", "warn"]

codes = [code for log in logs if (code := parse_error_code(log)) is not None and code > 10]
print(codes)  # [12, 45]
```

Ключевой момент: `parse_error_code(log)` вызывается **один раз** благодаря `:=` — без walrus пришлось бы вызывать функцию дважды (один раз для проверки, второй — для получения значения) либо городить вложенный цикл.

---

## Упражнение 2. Тернарный оператор

```python
def classify_score(score: int) -> str:
    return "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "F"

print(classify_score(95))  # A
print(classify_score(80))  # B
print(classify_score(65))  # C
print(classify_score(40))  # F
```

Вложенные тернарные операторы стоит использовать осторожно, потому что при увеличении числа условий строка превращается в трудночитаемую «простыню», где сложно быстро понять порядок проверки условий — в таких случаях лучше использовать обычный `if/elif/else`.

---

## Упражнение 3. Распаковка и `*args`/`**kwargs`

```python
def build_user(name, age, **extra):
    return {"name": name, "age": age, **extra}

print(build_user("Иван", 30, city="Москва", role="analyst"))
# {'name': 'Иван', 'age': 30, 'city': 'Москва', 'role': 'analyst'}

default_user = {"age": 18, "city": "Москва"}
custom_user = {**default_user, "age": 25}
print(custom_user)  # {'age': 25, 'city': 'Москва'}

records = [(1, "Аня"), (2, "Борис"), (3, "Вера")]
first, *rest = records
print(first)  # (1, 'Аня')
print(rest)   # [(2, 'Борис'), (3, 'Вера')]
```

---

## Упражнение 4. `zip`, `enumerate` и транспонирование

```python
products = ["Хлеб", "Молоко", "Сыр"]
prices = [45.5, 89.0, 320.0]

for i, (product, price) in enumerate(zip(products, prices), start=1):
    print(f"{i}. {product} — {price}")

matrix = [[1, 2], [3, 4], [5, 6]]
transposed = list(zip(*matrix))
print(transposed)  # [(1, 3, 5), (2, 4, 6)]
```

`zip(matrix)` (без звёздочки) получает **один** аргумент — сам список `matrix` — и просто упаковывает каждую его строку в кортеж из одного элемента: `[([1, 2],), ([3, 4],), ([5, 6],)]`. А `zip(*matrix)` распаковывает `matrix` в несколько отдельных аргументов (по одному на строку), и только тогда `zip` может объединить элементы по индексам, превращая строки в столбцы.

---

## Упражнение 5. Продвинутые f-строки

```python
revenue = 1834562.4567

print(f"{revenue:,.2f}")      # 1,834,562.46
print(f"{revenue:.2e}")       # 1.83e+06
print(f"{revenue:>15,.2f}")   # "   1,834,562.46" (ширина 15, выравнивание вправо)
print(f"{revenue=}")          # revenue=1834562.4567
```

---

## Упражнение 6. Декораторы

```python
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызов {func.__name__}(args={args}, kwargs={kwargs})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} вернула: {result}")
        return result
    return wrapper

def repeat(n=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(n)]
        return wrapper
    return decorator

@log_calls
@repeat(n=2)
def square(x):
    return x ** 2

square(4)
# Вызов square(args=(4,), kwargs={})
# square вернула: [16, 16]
```

Порядок применения: декораторы применяются **снизу вверх**. Сначала `square = repeat(n=2)(square)` — теперь `square` при вызове возвращает список из `n` результатов. Затем `square = log_calls(square)` — обёртка логирования оборачивает уже "размноженную" функцию, поэтому в логе видно вызов с одним набором аргументов, а результат — уже список из двух одинаковых значений.

---

## Упражнение 7. Типизация: `Optional`, `Literal`, `dataclass`

```python
from dataclasses import dataclass, field
from typing import Literal

catalog = {
    "SKU-1": {"name": "Клавиатура", "price": 2500},
    "SKU-2": {"name": "Мышь", "price": 900},
}

def find_product(sku: str) -> dict | None:
    return catalog.get(sku)

print(find_product("SKU-1"))  # {'name': 'Клавиатура', 'price': 2500}
print(find_product("SKU-99"))  # None

@dataclass
class Order:
    id: int
    status: Literal["new", "paid", "shipped", "cancelled"]
    total: float
    items: list[str] = field(default_factory=list)

o1 = Order(id=1, status="new", total=1500.0, items=["Клавиатура"])
o2 = Order(id=1, status="new", total=1500.0, items=["Клавиатура"])
print(o1 == o2)  # True — dataclass сравнивает по значению полей, а не по id объекта
```

---

## Упражнение 8. `Protocol` и `Generic`

```python
from typing import Protocol, Generic, TypeVar
import json

class Exportable(Protocol):
    def to_json(self) -> str: ...

class Item:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def to_json(self) -> str:
        return json.dumps({"name": self.name, "price": self.price})

def export_all(items: list[Exportable]) -> list[str]:
    return [item.to_json() for item in items]

print(export_all([Item("Стол", 5000.0), Item("Стул", 1500.0)]))

T = TypeVar("T")

class Queue(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        return self._items.pop(0)

q: Queue[int] = Queue()
q.enqueue(1)
q.enqueue(2)
print(q.dequeue())  # 1
```

`Item` не наследуется от `Exportable` явно — она подходит под протокол просто потому, что реализует метод `to_json`. Это и есть структурная типизация ("утиная типизация" с проверкой типов).

---

## Упражнение 9. Парадигмы: процедурный vs функциональный vs ООП

```python
orders = [
    {"customer": "Аня", "amount": 1200},
    {"customer": "Борис", "amount": 450},
    {"customer": "Аня", "amount": 300},
    {"customer": "Вера", "amount": 900},
]

# 1. Процедурный стиль
totals_proc = {}
for order in orders:
    customer = order["customer"]
    totals_proc[customer] = totals_proc.get(customer, 0) + order["amount"]
print(totals_proc)

# 2. Функциональный стиль
from functools import reduce
from collections import defaultdict

totals_func = reduce(
    lambda acc, order: {**acc, order["customer"]: acc.get(order["customer"], 0) + order["amount"]},
    orders,
    {}
)
print(totals_func)

# альтернатива через defaultdict
totals_func2 = defaultdict(int)
for customer, amount in ((o["customer"], o["amount"]) for o in orders):
    totals_func2[customer] += amount
print(dict(totals_func2))

# 3. ООП стиль
class RevenueAggregator:
    def __init__(self) -> None:
        self._totals: dict[str, float] = defaultdict(float)

    def add(self, order: dict) -> None:
        self._totals[order["customer"]] += order["amount"]

    def as_dict(self) -> dict[str, float]:
        return dict(self._totals)

aggregator = RevenueAggregator()
for order in orders:
    aggregator.add(order)
print(aggregator.as_dict())
```

Если появится требование учитывать валюту заказа, проще всего расширить **ООП-вариант**: достаточно добавить поле `currency` внутрь `RevenueAggregator` (например, хранить `_totals` как `dict[tuple[str, str], float]` или добавить конвертацию внутри метода `add`) — вся логика инкапсулирована в одном месте. В процедурном и функциональном вариантах пришлось бы переписывать саму функцию накопления и, скорее всего, весь вызывающий код, так как логика "размазана" по циклу/reduce, а не спрятана за интерфейсом класса.

---

## Упражнение 10. Dunder-методы, исключения и контекстные менеджеры

```python
from dataclasses import dataclass
from contextlib import contextmanager

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

print(Vector2D(1, 2) + Vector2D(3, 4))  # Vector2D(4, 6)


class NegativeAmountError(Exception):
    """Ошибка: сумма операции отрицательна."""


def withdraw(balance: float, amount: float) -> float:
    try:
        if amount < 0:
            raise NegativeAmountError(f"Сумма не может быть отрицательной: {amount}")
        if amount > balance:
            raise ValueError(f"Недостаточно средств: баланс {balance}, запрошено {amount}")
        result = balance - amount
    except NegativeAmountError as e:
        print(f"Ошибка отрицательной суммы: {e}")
        raise
    except ValueError as e:
        print(f"Ошибка баланса: {e}")
        raise
    else:
        print("Списание прошло успешно")
        return result
    finally:
        print("Операция withdraw завершена")


# Вариант через contextlib.contextmanager
@contextmanager
def suppress_negative():
    try:
        yield
    except NegativeAmountError as e:
        print(f"Подавлено: {e}")

with suppress_negative():
    withdraw(100, -50)
print("Код после with выполнился, исключение не всплыло")
```

Обратите внимание: `withdraw` внутри блока `except NegativeAmountError` делает `raise` (без аргументов), то есть пробрасывает исключение дальше — именно поэтому `suppress_negative` снаружи может его перехватить и подавить.