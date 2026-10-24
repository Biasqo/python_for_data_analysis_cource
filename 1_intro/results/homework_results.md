# Домашнее задание 1 — Решения

## 1. Анализ типов и truthy/falsy значений

| Выражение | Тип | `bool(...)` | Почему |
|-----------|-----|-------------|--------|
| `42` | `int` | `True` | Ненулевое число |
| `19.99` | `float` | `True` | Ненулевое число |
| `""` | `str` | `False` | Пустая строка |
| `"Python"` | `str` | `True` | Непустая строка |
| `[]` | `list` | `False` | Пустой список |
| `[0]` | `list` | `True` | Непустой список |
| `None` | `NoneType` | `False` | Отсутствие значения |
| `0` | `int` | `False` | Ноль |
| `0.001` | `float` | `True` | Ненулевое число |
| `False` | `bool` | `False` | Ложь |

## 2. Операторы `//` и `%`

Для числа:

```python
n = 157
```

Решение:

```python
print(n // 10)     # 15
print(n % 10)      # 7
print(n % 2 == 0)  # False
print(n % 5 == 0)  # False
```

Результат:

```text
Полных десятков: 15
Последняя цифра: 7
Чётное: False
Кратно 5: False
```

## 3. Работа с `None` и условными выражениями

### Часть 1

```python
print(get_name())
print(get_name(""))
print(get_name("Alice"))
print(get_name(0))
```

Результат:

```python
Anonymous
Anonymous
Alice
Anonymous
```

### Часть 2

`""` и `0` считаются ложными (*falsy*) значениями, поэтому условие:

```python
if not name:
```

выполняется для них так же, как и для `None`.

Основные falsy-значения:

```python
False
None
0
0.0
''
[]
{}
set()
()
range(0)
```

### Часть 3

Исправленная функция:

```python
def get_name(name: str=None):
    if name is None:
        return "Anonymous"
    return name
```

Теперь:

```python
get_name()        # "Anonymous"
get_name("")      # ""
get_name(0)       # 0
get_name("Alice") # "Alice"
```

## 4. Работа со списками и `enumerate`

Решение:

```python
countries = [
    "Germany",
    "France",
    "Italy",
    "Spain",
    "Portugal"
]

for i, country in enumerate(countries, start=1):
    print(f"{i}. {country}")

long_names = [c for c in countries if len(c) > 5]

letters_count = sum(len(c) for c in countries)
```

Результат:

```python
long_names = ['Germany', 'France', 'Portugal']
letters_count = 33
```

## 5. Мини-отчёт в JSON

Решение:

```python
import json

completed_tasks = int(input())

summary = {
    "student": "John Doe",
    "completed_tasks": completed_tasks,
    "score": completed_tasks * 20,
    "passed": completed_tasks * 20 >= 60,
}

with open("summary.json", "w") as f:
    json.dump(summary, f)

with open("summary.json") as f:
    loaded = json.load(f)

print(loaded["score"])
print(loaded["passed"])
```

Пример:

```text
Введите количество выполненных задач: 4

80
True
```

## Дополнительное задание

```python
def classify_temperature(temp: float) -> str:
    if temp < 0:
        return "freezing"
    elif temp < 15:
        return "cold"
    elif temp < 25:
        return "warm"
    return "hot"
```

Примеры:

```python
classify_temperature(-5)   # freezing
classify_temperature(10)   # cold
classify_temperature(20)   # warm
classify_temperature(30)   # hot
```