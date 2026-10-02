# Решения: Проверка блока 1

### 1. get_grade

```python
def get_grade(score: int) -> str:
    if score < 40:
        return "Неуд"
    if score < 60:
        return "Удовлетворительно"
    if score < 85:
        return "Хорошо"
    return "Отлично"
```

### 2. alternating_sum

```python
def alternating_sum(x: int, n: int) -> int:
    if n % 2 == 1:
        return x
    return 0
```

### 3. count_even_numbers

```python
def count_even_numbers(number: int) -> int:
    if number == 0:
        return 1

    count = 0
    while number > 0:
        digit = number % 10
        if digit % 2 == 0:
            count += 1
        number //= 10

    return count
```