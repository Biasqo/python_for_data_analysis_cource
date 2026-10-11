# Домашнее задание 2 — решения

> Python 3.10+. Только стандартная библиотека.
> Допущения там, где условие неоднозначно, указаны в комментариях к коду.

---

## 1. Банковские операции

```python
import csv
from statistics import mean
from typing import Any

# «Простая структура» — список словарей
Transaction = dict[str, Any]


def read_transactions(path: str = "transactions.csv") -> list[Transaction]:
    """Читает CSV и приводит значения к нужным типам."""
    with open(path, encoding="utf-8", newline="") as file:
        return [
            {
                "transaction_id": int(row["transaction_id"]),
                "client_id": int(row["client_id"]),
                "transaction_sum_roubles": float(row["transaction_sum_roubles"]),
                "purpose": row["purpose"],
                "card_type": row["card_type"],
                "transaction_datetime": row["transaction_datetime"],  # остаётся строкой
            }
            for row in csv.DictReader(file)
        ]


transactions: list[Transaction] = read_transactions()

# 1) Общая сумма
total_sum: float = sum(map(lambda t: t["transaction_sum_roubles"], transactions))

# 2) Сумма в разрезе типа карты (debit / credit)
sum_by_card_type: dict[str, float] = {
    card: sum(
        map(
            lambda t: t["transaction_sum_roubles"],
            filter(lambda t, c=card: t["card_type"] == c, transactions),
        )
    )
    for card in sorted({t["card_type"] for t in transactions})
}

# 3) Среднее значение суммы в разрезе purpose
avg_by_purpose: dict[str, float] = {
    purpose: mean(
        map(
            lambda t: t["transaction_sum_roubles"],
            filter(lambda t, p=purpose: t["purpose"] == p, transactions),
        )
    )
    for purpose in sorted({t["purpose"] for t in transactions})
}

print(total_sum)
print(sum_by_card_type)
print(avg_by_purpose)
```

---

## 2. Кеширование

```python
import time
from collections import OrderedDict


def _slow_square(number: int) -> int:
    time.sleep(3)
    return number * number


_square_cache: OrderedDict[int, int] = OrderedDict()


def cached_square(number: int) -> int:
    """Первый вызов с новым значением идёт в _slow_square, повторные — из кеша."""
    if number in _square_cache:
        return _square_cache[number]

    result = _slow_square(number)
    _square_cache[number] = result  # OrderedDict хранит значения в порядке добавления
    return result
```

---

## 3. Функции 1: позиционные аргументы

```python
def polynomial_formatter(*coefficients: float) -> str:
    """Коэффициенты от старшей степени к младшей -> строка уравнения '... = 0'."""
    degree = len(coefficients) - 1
    result = ""

    for index, coef in enumerate(coefficients):
        if coef == 0:
            continue

        power = degree - index
        number = f"{abs(coef):g}"  # 2.0 -> "2", 1.5 -> "1.5"

        if power == 0:
            term = number
        else:
            prefix = "" if abs(coef) == 1 else f"{number}*"
            term = prefix + ("x" if power == 1 else f"x^{power}")

        if not result:
            result = ("-" if coef < 0 else "") + term
        else:
            result += (" - " if coef < 0 else " + ") + term

    return f"{result or '0'} = 0"


# В условии имя написано с опечаткой — оставляем алиас
polynomal_formatter = polynomial_formatter


print(polynomial_formatter(3, 2, 1))   # 3*x^2 + 2*x + 1 = 0
print(polynomial_formatter(1, -2, 1))  # x^2 - 2*x + 1 = 0
print(polynomial_formatter(0, 2, 1))   # 2*x + 1 = 0
```

---

## 4. Функции 2: именованные аргументы

```python
from functools import partial
from typing import Any

# Transaction и transactions — из задания 1


def select_top_20(dataset: list[Transaction], **filters: Any) -> list[Transaction]:
    """Фильтрует по равенству полей (**filters), возвращает топ-20 по сумме."""
    filtered = filter(
        lambda t: all(t.get(key) == value for key, value in filters.items()),
        dataset,
    )
    return sorted(
        filtered,
        key=lambda t: t["transaction_sum_roubles"],
        reverse=True,
    )[:20]


# Чтобы вызывать так же, как в примерах из условия (без датасета):
top_20 = partial(select_top_20, transactions)

print(top_20(transaction_id=9))
print(top_20(purpose="Fuel", card_type="debit"))
```

---

## 5. Декоратор

```python
import functools
from typing import Any, Callable


def log_func_call(
    func: Callable[..., Any] | None = None,
    *,
    show_args: bool = True,
    show_result: bool = True,
) -> Callable[..., Any]:
    """Работает в обеих формах: @log_func_call и @log_func_call(show_args=False)."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if show_args:
                parts = [repr(a) for a in args]
                parts += [f"{key}={value!r}" for key, value in kwargs.items()]
                call = f"{f.__name__}({', '.join(parts)})"
            else:
                call = f"{f.__name__}(...)"

            print(f"Вызов: {call}")
            try:
                result = f(*args, **kwargs)
            except Exception as error:
                print(f"Ошибка: {call} -> {type(error).__name__}: {error}")
                raise  # исключение пробрасываем дальше (виден Traceback)

            shown = repr(result) if show_result else "..."
            print(f"Результат: {call} -> {shown}")
            return result

        return wrapper

    # @log_func_call без скобок
    if func is not None:
        return decorator(func)
    # @log_func_call(...) со скобками
    return decorator


@log_func_call
def add(a, b):
    return a + b


@log_func_call
def divide(a, b):
    return a / b


@log_func_call(show_args=False)
def secret(token, *, key=None):
    return "ok"


add(2, 3)
# Вызов: add(2, 3)
# Результат: add(2, 3) -> 5

secret("abc", key=1)
# Вызов: secret(...)
# Результат: secret(...) -> 'ok'

divide(10, 0)
# Вызов: divide(10, 0)
# Ошибка: divide(10, 0) -> ZeroDivisionError: division by zero
# Traceback ...
```

---

## 6. ООП

### Связь между классами

`LinearSpaceElement` — абстрактный базовый класс, описывающий **элемент линейного (векторного) пространства**. Он фиксирует интерфейс, который обязан поддерживать любой такой элемент: сложение элементов, умножение на число и взятие противоположного элемента. Через эти три операции в базовом классе выражены остальные: вычитание (`a - b = a + (-b)`), умножение числа на элемент слева (`2 * a`) и деление на число (`a / k = a * (1/k)`).

`Vector2D` **наследуется** от `LinearSpaceElement` («является элементом линейного пространства») и реализует абстрактные методы для пары `(x, y)`. Дополнительно у него есть то, что специфично для евклидова пространства: скалярное произведение и длина. Благодаря наследованию любой другой тип (`Vector3D`, многочлен, матрица) можно описать тем же интерфейсом.

```python
from __future__ import annotations

import math
from abc import ABC, abstractmethod


class LinearSpaceElement(ABC):
    """Элемент линейного пространства: сложение, умножение на число, противоположный."""

    @abstractmethod
    def __add__(self, other: LinearSpaceElement) -> LinearSpaceElement: ...

    @abstractmethod
    def __mul__(self, scalar: float) -> LinearSpaceElement: ...

    @abstractmethod
    def __neg__(self) -> LinearSpaceElement: ...

    # --- операции, выраженные через абстрактные ---
    def __sub__(self, other: LinearSpaceElement) -> LinearSpaceElement:
        return self + (-other)

    def __rmul__(self, scalar: float) -> LinearSpaceElement:
        return self * scalar

    def __truediv__(self, scalar: float) -> LinearSpaceElement:
        return self * (1 / scalar)  # при scalar == 0 -> ZeroDivisionError


class Vector2D(LinearSpaceElement):
    __slots__ = ("x", "y")  # ровно две внутренние переменные

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: LinearSpaceElement) -> Vector2D:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def dot(self, other: Vector2D) -> float:
        """Скалярное произведение."""
        return self.x * other.x + self.y * other.y

    __matmul__ = dot  # a @ b

    def length(self) -> float:
        """Длина (евклидова норма) вектора."""
        return math.hypot(self.x, self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Vector2D({self.x!r}, {self.y!r})"


a = Vector2D(3, 4)
b = Vector2D(1, 2)

print(a + b)      # Vector2D(4, 6)
print(a - b)      # Vector2D(2, 2)
print(a * 2)      # Vector2D(6, 8)
print(2 * a)      # Vector2D(6, 8)
print(a / 2)      # Vector2D(1.5, 2.0)
print(a.dot(b))   # 11
print(a.length()) # 5.0
```

---

## 7. Классы и функции при работе с API

```python
import random
import string
from dataclasses import dataclass
from typing import Callable


# --- заданный код (не менять) ---
def _make_user(user_id: int) -> dict:
    return {
        "id": user_id,
        "name": "".join(random.choices(string.ascii_uppercase, k=5)),
        "age": random.randint(18, 60),
        "email": "".join(random.choices(string.ascii_lowercase, k=6)) + "@gmail.com",
    }


def fetch_users(user_id: int | None = None) -> list[dict]:
    if user_id is None:
        ids = range(1, random.randint(2, 6))
    elif random.random() < 0.2:
        return []
    else:
        ids = [user_id]

    return [_make_user(i) for i in ids]
# --- конец заданного кода ---


@dataclass(frozen=True)
class User:
    id: int
    name: str
    age: int
    email: str


def user_factory(
    api_func: Callable[[int | None], list[dict]],
) -> Callable[[int | None], list[User]]:
    """Оборачивает API-функцию: dict'ы из ответа превращает в объекты User.
    Результат всегда list[User] (пустой список, если API ничего не вернул)."""
    return lambda user_id=None: [User(**raw) for raw in api_func(user_id)]


get_users = user_factory(fetch_users)

all_users: list[User] = get_users()                    # все пользователи
user_101: list[User] = get_users(101)                  # пользователь с id=101 (или [])
older_than_20: list[User] = list(
    filter(lambda u: u.age > 20, get_users())          # пользователи с age > 20
)

print(all_users)
print(user_101)
print(older_than_20)
```

---

## 8. Банковский счёт

```python
class InsufficientFundsError(Exception):
    """Недостаточно средств на счёте."""

    def __init__(self, balance: float, amount: float) -> None:
        super().__init__(
            f"Недостаточно средств: баланс {balance}, запрошено {amount}"
        )
        self.balance = balance
        self.amount = amount


class BankAccount:
    def __init__(self, owner: str) -> None:
        self.owner = owner
        self._balance: float = 0
        self._history: list[str] = []

    # --- баланс только для чтения ---
    @property
    def balance(self) -> float:
        return self._balance

    # --- операции ---
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount
        self._history.append(f"deposit {amount}")

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount
        self._history.append(f"withdraw {amount}")

    # --- магические методы ---
    def __iadd__(self, amount: float) -> "BankAccount":   # acc += 500
        self.deposit(amount)
        return self

    def __isub__(self, amount: float) -> "BankAccount":   # acc -= 200
        self.withdraw(amount)
        return self

    def __str__(self) -> str:
        return f"Счёт {self._genitive(self.owner)}: {self._balance} руб."

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance!r})"

    def __len__(self) -> int:       # количество операций
        return len(self._history)

    def __bool__(self) -> bool:     # True, если на счёте есть деньги
        return self._balance > 0

    def __iter__(self):             # итерация по истории операций
        return iter(self._history)

    @staticmethod
    def _genitive(name: str) -> str:
        """Упрощённый родительный падеж для имён (Иван -> Ивана)."""
        endings = {"й": "я", "ь": "я", "а": "ы", "я": "и"}
        last = name[-1]
        if last in endings:
            return name[:-1] + endings[last]
        if last.lower() in "бвгджзклмнпрстфхцчшщ":
            return name + "а"
        return name


acc = BankAccount("Иван")
acc.deposit(1000)
acc += 500
acc -= 200

print(acc)              # Счёт Ивана: 1300 руб.
print(acc.balance)      # 1300
print(len(acc))         # 3
print(bool(acc))        # True
print(list(acc))        # ['deposit 1000', 'deposit 500', 'withdraw 200']

try:
    acc.withdraw(5000)
except InsufficientFundsError:
    print("Недостаточно средств")
```