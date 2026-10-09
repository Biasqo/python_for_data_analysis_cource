# Домашнее задание 2

#### 5. Реализуйте декоратор `@log_func_call`, который логирует каждый вызов декорируемой функции.
* Перед вызовом функции декоратор печатает строку вида: `Вызов: имя_функции(арг1, арг2, ключ=значение)`
* После успешного вызова печатает строку вида: `Результат: имя_функции(...) -> значение`
* Если функция выбросила исключение - выводим: `Ошибка: имя_функции(...) -> ТипИсключения: сообщение`
* (*Задание со звездочкой*) Добавьте параметр `@log_func_call(show_args=True, show_result=True)`, чтобы можно было включать/выключать вывод аргументов и результата независимо друг от друга.

**Пример использования:**
```python
@log_func_call
def add(a, b):
    return a + b

@log_func_call
def divide(a, b):
    return a / b

add(2, 3)
# Вызов: add(2, 3)
# Результат: add(2, 3) -> 5

divide(10, 0)
# Вызов: divide(10, 0)
# Ошибка: divide(10, 0) -> ZeroDivisionError: division by zero
# Traceback ...
```

#### 6. Реализуйте классы: `LinearSpaceElement`, `Vector2D` (вектор в двумерном пространстве) свяжите их (подумайте как)
В `markdown` ячейке или файле объясните связь между классами. \
Класс `Vector2D` имеет всего 2 внутренние переменные `x` и `y`.\
Класс `Vector2D` должен поддерживать:
* Сложение вычитание векторов 
* Умножение и деление вектора на число
* Скалярное произведение векторов
* Вывод длины вектора (через метод)

**Создание вектора:**
```python
a = Vector2D(3, 4)
b = Vector2D(1, 2)
```

**Сложение и вычитание векторов:**
```python
a + b   # Vector2D(4, 6)
a - b   # Vector2D(2, 2)
```

#### 7. Классы и функции при работе с API

Дана функция `fetch_users`, которая имитирует вызов API. \
Функции `fetch_users` и `_make_user` **нельзя менять**.

```python
import random
import string

def _make_user(user_id: int) -> dict:
    return {
        "id": user_id,
        "name": "".join(random.choices(string.ascii_uppercase, k=5)),
        "age": random.randint(18, 60),
        "email": "".join(random.choices(string.ascii_lowercase, k=6)) + "@mail.com",
    }


def fetch_users(user_id: int | None = None) -> list[dict]:
    if user_id is None:
        ids = range(1, random.randint(2, 6))
    elif random.random() < 0.2:
        return []
    else:
        ids = [user_id]

    return [_make_user(i) for i in ids]
```

* Реализуйте класс `User`
* Реализуйте функцию `user_factory`, которая принимает на вход API-функцию `fetch_users`
* Используя `user_factory` лямбду, получите:
   * список всех пользователей;
   * пользователя с `id=101`;
   * пользователей у которых `age>20`;

**Пример использования:**
```python
get_users = user_factory(fetch_users)

all_users = get_users()          # [User(...), User(...), ...]
one_user  = get_users(2)         # User(id=2, ...) или None
nobody    = get_users(99)        # User(id=99, ...) или None
```

#### 8. Банковский счёт

Реализуйте два класса: `BankAccount` и своё исключение `InsufficientFundsError`.

**Класс `BankAccount`**:
* Переменные: `owner`, `_balance` (баланс должен быть приватным)
* Методы: `deposit` - пополнение, `withdraw` - снятие со счёта (при нехватке средств нужно выдать ошибку)
* Переопределены магические методы

**Класс исключения:**
```python
class InsufficientFundsError(Exception):
    pass
```

**Пример**
```python
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