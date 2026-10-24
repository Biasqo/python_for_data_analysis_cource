# Глава 3 - Домашнее задание. Ответы

---

## Задание 1. Выбор структуры данных

a) **`tuple`** - координаты (x, y) не меняются, а неизменяемость - именно то, что должно быть гарантировано для такого рода данных. Плюс `tuple` хешируем и может быть ключом словаря, если понадобится.

b) **`set`** - нужна быстрая проверка вхождения (O(1)) и автоматическое отсутствие дубликатов, порядок не важен.

c) **`list`** - важен порядок посещений и допускаются повторы (одна и та же страница может быть открыта несколько раз).

d) **`dict`** - классическое сопоставление "ключ → значение" с быстрым доступом по коду страны.

---

## Задание 2. `is` vs `==`

```python
print(a == b)     # True  - одинаковое содержимое
print(a is b)     # False - разные объекты в памяти
print(a is c)     # True  - c ссылается на тот же объект, что и a
print(a == c)     # True  - содержимое одинаковое (и это тот же объект)
```

`a == b` возвращает `True`, потому что `==` сравнивает **значения** списков поэлементно, а они совпадают. `a is not b` - потому что `a` и `b` созданы как два разных объекта в памяти (два отдельных вызова литерала `[1, 2, 3]`), несмотря на одинаковое содержимое.

---

## Задание 3. Хешируемость

Ошибка: `TypeError: unhashable type: 'list'`.

Нарушено правило: **ключом словаря может быть только неизменяемый (immutable) и хешируемый объект**. `list` - изменяемый тип, поэтому не хешируется (если бы список изменился после использования как ключ, хеш "устарел" бы, и словарь сломался бы).

Исправление - использовать `tuple` вместо `list`:

```python
students = {}
grades = (5, 4, 5)
students[grades] = "Иванов"
```

---

## Задание 4. Поверхностное копирование и алиасинг

Вывод:

```python
{'name': 'Анна', 'scores': [80, 90, 70, 100]}
{'name': 'Мария', 'scores': [80, 90, 70, 100]}
```

Объяснение: `copy.copy()` создаёт новый словарь верхнего уровня, но вложенный `list` `scores` остаётся **общим** для `original` и `shallow` (алиасинг). Поэтому `shallow["scores"].append(100)` меняет список, видимый из обоих словарей. А вот `shallow["name"] = "Мария"` не влияет на `original["name"]`, так как строка присваивается новому ключу верхнего уровня словаря `shallow`, а не изменяет общий объект.

Схема:

```
original ──► {"name": "Анна",  "scores": ──┐
                                            ▼
shallow  ──► {"name": "Мария", "scores": ──┴──► [80, 90, 70, 100]  (общий список)
```

---

## Задание 5. Матрица и ловушка алиасинга

Проблема: `[[0] * 3] * 3` создаёт **один** внутренний список `[0, 0, 0]`, а затем трижды дублирует **ссылку** на него. В результате все три "строки" матрицы - это один и тот же объект, поэтому изменение `matrix[0][0]` отражается во всех строках:

```python
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)
# [[1, 0, 0], [1, 0, 0], [1, 0, 0]]  - изменились все строки!
```

Правильная версия - создать независимые списки с помощью list comprehension:

```python
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print(matrix)
# [[1, 0, 0], [0, 0, 0], [0, 0, 0]]  - только первая строка изменилась
```

---

## Задание 6. `Counter`

```python
from collections import Counter
import re

def most_frequent_word(text: str) -> str:
    words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
    counter = Counter(words)
    return counter.most_common(1)[0][0]

# Пример:
text = "Кот сидел на окне. Кот смотрел на птиц, а кот мурлыкал."
print(most_frequent_word(text))
# "кот"
```

---

## Задание 7. `defaultdict`

Суммы по категориям:

```python
from collections import defaultdict

purchases = [
    ("еда", 350),
    ("транспорт", 100),
    ("еда", 200),
    ("развлечения", 500),
    ("транспорт", 50),
]

totals = defaultdict(int)
for category, amount in purchases:
    totals[category] += amount

print(dict(totals))
# {'еда': 550, 'транспорт': 150, 'развлечения': 500}
```

Группировка в списки:

```python
groups = defaultdict(list)
for category, amount in purchases:
    groups[category].append(amount)

print(dict(groups))
# {'еда': [350, 200], 'транспорт': [100, 50], 'развлечения': [500]}
```

---

## Задание 8. `namedtuple`

```python
from collections import namedtuple

Student = namedtuple("Student", ["name", "age", "grade"])

students = [
    Student("Анна", 20, 4.8),
    Student("Борис", 21, 4.2),
    Student("Вера", 19, 4.9),
]

# 1. Сортировка по grade по убыванию
sorted_students = sorted(students, key=lambda s: s.grade, reverse=True)
print(sorted_students)
# [Student(name='Вера', age=19, grade=4.9),
#  Student(name='Анна', age=20, grade=4.8),
#  Student(name='Борис', age=21, grade=4.2)]

# 2. Имена студентов с grade >= 4.5
top_names = [s.name for s in students if s.grade >= 4.5]
print(top_names)
# ['Анна', 'Вера']
```

---

## Задание 9. LRU-кэш вручную

```python
from collections import OrderedDict

class SimpleLRUCache:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            evicted_key, _ = self.cache.popitem(last=False)
            print(f"Вытеснен: {evicted_key}")

# Демонстрация:
lru = SimpleLRUCache(capacity=3)
lru.put("a", 1)       # cache: {a}
lru.put("b", 2)       # cache: {a, b}
lru.put("c", 3)       # cache: {a, b, c}
lru.get("a")          # a становится "самым свежим" -> порядок: {b, c, a}
lru.put("d", 4)       # cache полон -> вытесняется "b" (наименее недавно использованный)
                      # Вывод: "Вытеснен: b"
print(list(lru.cache.items()))
# [('c', 3), ('a', 1), ('d', 4)]
```

---

## Задание 10. Рекурсия и сложность

a) Функция `mystery(n)` считает, **сколько раз можно поделить `n` на 2 (целочисленно), пока не получится значение ≤ 1** - то есть вычисляет `⌊log₂(n)⌋`.

Примеры:
```python
mystery(1)   # 0
mystery(8)   # 3   (8 -> 4 -> 2 -> 1)
mystery(16)  # 4   (16 -> 8 -> 4 -> 2 -> 1)
```

b) Временная сложность: **O(log n)**.

Обоснование: на каждом вызове аргумент уменьшается вдвое (`n // 2`), а работа на каждом уровне - константная (O(1): сравнение и сложение). Рекуррентное соотношение: `T(n) = T(n/2) + C`. Разворачивая: на уровне `k` аргумент равен `n / 2^k`; рекурсия останавливается, когда `n / 2^k ≈ 1`, то есть `k = log₂(n)`. Значит, общее число вызовов (и, соответственно, время работы) пропорционально `log₂(n)`, то есть `O(log n)`.

c) Итеративная версия:

```python
def mystery_iterative(n):
    count = 0
    while n > 1:
        n = n // 2
        count += 1
    return count
```