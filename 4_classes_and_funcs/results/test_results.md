# Решения: проверка блоков 3-4

Все решения используют только стандартную библиотеку и проверены на примерах из условия.

---

## Задание 1. `*args` и `**kwargs`

### Идея

* `*dicts` собирает все позиционные аргументы в кортеж словарей.
* `**overrides` собирает именованные аргументы в словарь.
* Создаём **новый** пустой словарь и по очереди обновляем его методом `update`. Так более поздний словарь перезаписывает значения более раннего, а исходные словари не меняются.
* `overrides` применяем последними, поэтому они имеют наивысший приоритет.
* Если ничего не передано, цикл не выполнится, и вернётся пустой `dict`.

### Решение

```python
from typing import Any


def merge_dicts(*dicts: dict, **overrides: Any) -> dict:
    result: dict = {}
    for d in dicts:
        result.update(d)        # правый словарь перезаписывает левый
    result.update(overrides)    # именованные аргументы - последними
    return result
```

### Проверка

```python
merge_dicts({"a": 1}, {"b": 2}, a=10)          # {'a': 10, 'b': 2}
merge_dicts({"a": 1, "b": 1}, {"b": 2})        # {'a': 1, 'b': 2}
merge_dicts()                                  # {}
```

### Альтернатива

То же самое одной строкой через распаковку:

```python
def merge_dicts(*dicts: dict, **overrides: Any) -> dict:
    return {k: v for d in (*dicts, overrides) for k, v in d.items()}
```

---

## Задание 2. Декоратор с повтором

### Идея

Декоратор с параметрами - это **три уровня вложенности**:

1. `retry(times, exceptions)` принимает параметры и возвращает декоратор.
2. `decorator(func)` принимает функцию и возвращает обёртку.
3. `wrapper(*args, **kwargs)` вызывает функцию с повторами.

Логика в `wrapper`:

* делаем до `times` попыток в цикле;
* при успехе сразу возвращаем результат;
* если поймали исключение из `exceptions` и это **последняя** попытка, пробрасываем его через `raise`. Так сохраняется оригинальный traceback;
* исключения, которых нет в `exceptions`, не перехватываются и вылетают сразу, без повторов;
* `@functools.wraps(func)` копирует `__name__` и `__doc__` в обёртку, иначе `fetch.__name__` был бы `'wrapper'`.

`times` считается как **общее число попыток**: `times=3` значит максимум три вызова функции (как в условии: «3 неудачи подряд»).

### Решение

```python
import functools
from typing import Any, Callable


def retry(
    times: int,
    exceptions: tuple[type[BaseException], ...],
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise       # попытки закончились - пробрасываем последнее исключение
        return wrapper
    return decorator
```

### Проверка

```python
import random


@retry(times=3, exceptions=(ConnectionError,))
def fetch():
    outcome = random.choice(["success", "error1", "error2", "error3"])

    if outcome == "success":
        return {"status": "ok", "data": "some payload"}

    if outcome == "error1":
        raise ValueError("Error 1: invalid input")

    if outcome == "error2":
        raise RuntimeError("Error 2: server failure")

    raise ConnectionError("Error 3: network unreachable")


print(fetch.__name__)   # fetch
fetch()
# {'status': 'ok', 'data': 'some payload'}   - успех (с 1-й, 2-й или 3-й попытки)
# ConnectionError: Error 3: network unreachable   - 3 неудачи подряд
# ValueError: Error 1: invalid input         - сразу, без повторов
# RuntimeError: Error 2: server failure      - сразу, без повторов
```

Детерминированная проверка без случайности:

```python
calls = 0


@retry(times=3, exceptions=(ConnectionError,))
def flaky():
    global calls
    calls += 1
    if calls < 3:
        raise ConnectionError("нет связи")
    return "ok"


print(flaky(), calls)   # ok 3
```

---

## Задание 3. Класс `Money`

### Идея

Каждая возможность из условия соответствует магическому методу:

| Требование | Метод |
|---|---|
| `a + b` | `__add__` |
| `a - b` | `__sub__` |
| `sum([...])` | `__radd__` |
| `==` | `__eq__` |
| `<`, `>` | `__lt__`, `__gt__` |
| `repr` | `__repr__` |

Важные моменты:

* **Проверка валюты.** Вынесена в `_check`, чтобы не дублировать код в `+`, `-`, `<`, `>`. При разных валютах выбрасывается собственное исключение `CurrencyMismatchError`.
* **`sum`.** Он начинает с числа `0` и делает `0 + Money(...)`. У `int` нет такой операции для `Money`, поэтому Python вызывает у правого операнда `__radd__`. Если `other == 0`, возвращаем сам объект, и цепочка складывается дальше.
* **Сравнение с другим типом.** Если `other` не `Money`, возвращаем `NotImplemented`, а не бросаем ошибку. Тогда Python пробует обратную операцию, а потом применяет поведение по умолчанию. Для `==` результат будет `False` без исключения.
* **`print`.** Если нет `__str__`, `print` использует `__repr__`, поэтому `print(Money(5, "RUB"))` выводит `Money(5, 'RUB')`.
* **`!r` в f-строке** вызывает `repr`, поэтому строка валюты получает кавычки: `'RUB'`.

### Решение

```python
class CurrencyMismatchError(Exception):
    """Попытка выполнить операцию над деньгами в разных валютах."""


class Money:
    def __init__(self, amount: float, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def _check(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"{self.currency} != {other.currency}")

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other: object) -> "Money":
        # нужен для sum(): первое сложение выглядит как 0 + Money(...)
        if other == 0:
            return self
        return NotImplemented

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self.amount < other.amount

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self.amount > other.amount

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"
```

### Проверка

```python
Money(5, "RUB") + Money(3, "RUB")              # Money(8, 'RUB')
Money(5, "RUB") - Money(3, "RUB")              # Money(2, 'RUB')
Money(5, "RUB") + Money(3, "USD")              # CurrencyMismatchError

Money(1, "RUB") == Money(1, "RUB")             # True
Money(1, "RUB") < Money(2, "RUB")              # True
Money(1, "RUB") == 1                           # False (без ошибки)

sum([Money(1, "RUB"), Money(2, "RUB")])        # Money(3, 'RUB')
print(Money(5, "RUB"))                         # Money(5, 'RUB')
```

### Замечание

Когда в классе определён `__eq__`, Python автоматически делает объект нехешируемым (`__hash__ = None`), то есть `Money` нельзя положить в `set` или использовать как ключ `dict`. В условии этого не требуется. Если понадобится, нужно добавить:

```python
def __hash__(self) -> int:
    return hash((self.amount, self.currency))
```

---

## Задание 4. Генераторы: чтение больших логов

### Идея

Каждая функция - генератор: она обрабатывает **одну строку за раз** и передаёт её дальше по цепочке. Благодаря этому файл никогда не загружается в память целиком, и работа останавливается, как только набрано нужное число записей.

```text
read_lines  ->  parse_log  ->  filter_level  ->  фильтр по модулю  ->  islice(10)
 (строки)       (dict)          (только ERROR)    (только payments)    (первые 10)
```

* **`read_lines`.** Файл открывается через `with`, а цикл `for line in f` читает его построчно. Файл закроется сам, когда генератор будет исчерпан или закрыт.
* **`parse_log`.** Строка делится по разделителю `" - "` с ограничением `maxsplit=3`. Так сообщение, содержащее ` - `, не разобьётся на лишние части. Миллисекунды (`,123`) отбрасываются через `split(",")[0]`, чтобы ключ `datetime` совпал с форматом из условия. Некорректные строки пропускаются.
* **`filter_level`.** Генераторное выражение, которое пропускает только записи с нужным уровнем.
* **Конвейер.** Фильтр по модулю задаётся ещё одним генераторным выражением. `itertools.islice(..., 10)` берёт первые 10 записей и останавливает всю цепочку, так что остаток файла даже не читается.

### Решение

```python
import itertools
from typing import Iterable, Iterator


def read_lines(path: str) -> Iterator[str]:
    """Лениво отдаёт строки файла."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def parse_log(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """Превращает строки лога в словари."""
    for line in lines:
        parts = line.split(" - ", 3)
        if len(parts) != 4:          # пустая или повреждённая строка
            continue
        dt, level, module, message = parts
        yield {
            "datetime": dt.split(",")[0],   # отбрасываем миллисекунды
            "level": level,
            "module": module,
            "message": message,
        }


def filter_level(records: Iterable[dict], level: str) -> Iterator[dict]:
    """Оставляет записи с нужным уровнем."""
    return (r for r in records if r["level"] == level)
```

### Конвейер

```python
records = parse_log(read_lines("app.log"))
errors = filter_level(records, "ERROR")
payments_errors = (r for r in errors if r["module"] == "payments")

for record in itertools.islice(payments_errors, 10):
    print(record)
```

### Проверка

```python
next(parse_log(["2026-06-04 00:50:14,123 - ERROR - payments - Card declined"]))
# {'datetime': '2026-06-04 00:50:14', 'level': 'ERROR',
#  'module': 'payments', 'message': 'Card declined'}
```

```python
# Вывод конвейера (не более 10 строк):
# {'datetime': '2026-06-04 00:50:14', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
# {'datetime': '2026-06-04 02:13:40', 'level': 'ERROR', 'module': 'payments', 'message': 'Timeout'}
# ...
```