# Проверка блоков 3-4
```text
Задания оцениваются в 2 балла
Решение нужно сдать только файлом (или несколькими файлами) `ipynb`, `.py`
```

## Задание 1. `*args` и `**kwargs`

Напишите функцию `merge_dicts(*dicts, **overrides)`, которая объединяет словари **слева направо**. При совпадении ключей значение подставляется из словаря **справа**, а именованные аргументы `overrides` применяются последними.

* Исходные словари не изменяются.
* Если ничего не передано, возвращается пустой `dict`.

**Примеры:**
```python
merge_dicts({"a": 1}, {"b": 2}, a=10)          # {'a': 10, 'b': 2}
merge_dicts({"a": 1, "b": 1}, {"b": 2})        # {'a': 1, 'b': 2}
merge_dicts()                                  # {}
```

Используйте только стандартные библиотеки.

## Задание 2. Декоратор с повтором

Дана функция:
```python
import random

def fetch():
    outcome = random.choice(["success", "error1", "error2", "error3"])

    if outcome == "success":
        return {"status": "ok", "data": "some payload"}

    if outcome == "error1":
        raise ValueError("Error 1: invalid input")

    if outcome == "error2":
        raise RuntimeError("Error 2: server failure")

    raise ConnectionError("Error 3: network unreachable")
```

Напишите декоратор `retry(times, exceptions)`. Он повторяет вызов функции при исключениях из `exceptions`, но не более `times` раз. Если все попытки неудачны, пробрасывается последнее исключение.

**Примеры:**
```python
attempts = 0

@retry(times=3, exceptions=(ConnectionError,))
def fetch():
    ...  # тело функции то же, что выше

# Возможные результаты выполнения
fetch()            # {'status': 'ok', 'data': 'some payload'}        - успех (с 1-й, 2-й или 3-й попытки)
fetch()            # ConnectionError: Error 3: network unreachable   - 3 неудачи подряд
fetch()            # ValueError: Error 1: invalid input              - выбрасывается сразу 
fetch()            # RuntimeError: Error 2: server failure           - выбрасывается сразу
fetch.__name__     # 'fetch'
```

```python
@retry(times=5, exceptions=(ConnectionError, RuntimeError))
def fetch():
    ... # тело функции то же, что выше

fetch()            # ValueError пробрасывается сразу, а ConnectionError и RuntimeError повторяются до 5 раз
```

Используйте только стандартные библиотеки.

## Задание 3. Класс `Money`

Реализуйте класс `Money(amount, currency)`, который поддерживает:

* сложение и вычитание (только для одинаковой валюты, иначе `CurrencyMismatchError` - собственный класс ошибок);
* операторы сравнения `==`, `<`, `>`;
* `sum([Money(1, "RUB"), Money(2, "RUB")])`;
* `repr` вида `Money(1, 'RUB')`;

**Примеры:**
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

Используйте только стандартные библиотеки.

## Задание 4. Генераторы: чтение больших логов

Дан лог-файл `app.log` (приложен к заданию). Каждая строка имеет вид:

```text
2026-06-04 00:50:14,123 - ERROR - payments - Card declined
2026-06-04 00:51:02,121 - INFO - auth - User logged in
```

Реализуйте цепочку функций-генераторов, **не загружая файл в память целиком**:

* `read_lines(path)` - лениво отдаёт строки файла;
* `parse_log(lines)` - отдаёт для каждой строки `dict` с ключами `datetime`, `level`, `module`, `message`;
* `filter_level(records, level)` - оставляет только записи с нужным уровнем.

Соберите из них конвейер, который выводит первые 10 записей уровня `ERROR` из модуля `payments`.
```text
# {'datetime': '2026-06-04 00:50:14', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
# {'datetime': '2026-06-04 00:51:47', 'level': 'ERROR', 'module': 'payments', 'message': 'Insufficient funds'}
# {'datetime': '2026-06-04 00:53:21', 'level': 'ERROR', 'module': 'payments', 'message': 'Card expired'}
# {'datetime': '2026-06-04 00:54:32', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
# {'datetime': '2026-06-04 00:56:19', 'level': 'ERROR', 'module': 'payments', 'message': 'Transaction timeout'}
# {'datetime': '2026-06-04 00:57:34', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
# {'datetime': '2026-06-04 00:59:18', 'level': 'ERROR', 'module': 'payments', 'message': 'Insufficient funds'}
# {'datetime': '2026-06-04 01:00:23', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
# {'datetime': '2026-06-04 01:02:19', 'level': 'ERROR', 'module': 'payments', 'message': 'Card expired'}
# {'datetime': '2026-06-04 01:03:31', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
```

**Примеры:**

`read_lines`:
```python
lines = read_lines("app.log")
next(lines)    # '2026-06-04 00:50:14,123 - ERROR - payments - Card declined'
next(lines)    # '2026-06-04 00:51:02,121 - INFO - auth - User logged in'
next(lines)    # '2026-06-04 00:51:47,456 - ERROR - payments - Insufficient funds'
```

`parse_log`:
```python
records = parse_log(read_lines("app.log"))
next(records)  # {'datetime': '2026-06-04 00:50:14', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
next(records)  # {'datetime': '2026-06-04 00:51:02', 'level': 'INFO', 'module': 'auth', 'message': 'User logged in'}
next(records)  # {'datetime': '2026-06-04 00:51:47', 'level': 'ERROR', 'module': 'payments', 'message': 'Insufficient funds'}
```

`filter_level`:
```python
errors = filter_level(parse_log(read_lines("app.log")), "ERROR")
next(errors)   # {'datetime': '2026-06-04 00:50:14', 'level': 'ERROR', 'module': 'payments', 'message': 'Card declined'}
next(errors)   # {'datetime': '2026-06-04 00:51:47', 'level': 'ERROR', 'module': 'payments', 'message': 'Insufficient funds'}

warnings = filter_level(parse_log(read_lines("app.log")), "WARNING")
next(warnings) # {'datetime': '2026-06-04 00:52:58', 'level': 'WARNING', 'module': 'api', 'message': 'Rate limit approaching'}

list(filter_level(parse_log(read_lines("app.log")), "DEBUG"))   # []
```

Используйте только стандартные библиотеки.