# Глава 4 - тест

## Задание 1. Предскажите вывод

```python
values = [1, 2, 3, 4, 5]
result = [y for x in values if (y := x ** 2) > 10]
print(result)
```

## Задание 2. Найдите ошибку

Что произойдёт при выполнении этого кода? Объясните ошибку одним предложением.

```python
def greet(name: str, age: int = 18, city) -> str:
    return f"{name}, {age}, {city}"
```

## Задание 3. `Optional` или `Union`?

Чем `Optional[str]` отличается от `Union[str, int]`? Приведите пример ситуации, когда уместен именно `Optional`.

## Задание 4. Предскажите вывод

```python
matrix = [[1, 2, 3], [4, 5, 6]]
print(list(zip(matrix)))
print(list(zip(*matrix)))
```

## Задание 5. Заполните пропуски в таблице

| Конструкция | Что делает | Пример |
|---|---|---|
| `first, *rest = [1, 2, 3, 4]` | ??? | `first = ???`, `rest = ???` |
| `*init, last = [1, 2, 3, 4]` | ??? | `init = ???`, `last = ???` |
| `{**d1, **d2}` | ??? | ??? |
| `func(*args)` | ??? | ??? |

## Задание 6. Порядок выполнения декораторов - быстрый ответ

```python
def retry(times=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return decorator

@retry(times=5)
def fetch(): ...
```

Чему эквивалентна строка `@retry(times=5)`? Запишите в одну строку без декоратора.

## Задание 7. `dataclass` - быстрый ответ

Что выведет следующий код?

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1 == p2)
print(p1 is p2)
```

## Задание 8. Наследование vs композиция

Перепишите этот код так, чтобы `ReportBuilder` использовал **композицию** вместо наследования (то есть получал агрегатор через конструктор, а не наследовался от него):

```python
class BaseAggregator:
    def __init__(self):
        self._totals = {}

    def add(self, category, amount):
        self._totals[category] = self._totals.get(category, 0) + amount

class ReportBuilder(BaseAggregator):
    def build(self):
        return "\n".join(f"{k}: {v}" for k, v in self._totals.items())
```

## Задание 9. `try/except/else/finally` - предскажите вывод

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Деление на ноль")
        return None
    else:
        print("Успех")
    finally:
        print("Завершено")
    return result

divide(10, 0)
```

## Задание 10. Контекстный менеджер - базовый случай

В следующем контекстном менеджере пропущена очистка ресурса. Допишите его так, чтобы сообщение о завершении печаталось **всегда**, даже если внутри блока `with` возникло исключение:

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.perf_counter()
    yield
    # допишите очистку здесь
```

Что произойдёт, если оставить код без изменений и внутри блока `with` возникнет исключение?