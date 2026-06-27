
## Проверка

**Короткий тест — 5 вопросов (проводится на 83-й минуте, перед объяснением домашнего задания):**

### 1. Что выведет `bool([0])`? Почему?

**Ответ:** `True` — список, содержащий хотя бы один элемент, считается истинным (*truthy*), независимо от значения этого элемента.

---

### 2. Какая ошибка есть в этом коде?

```python
def append_item(val, lst=[]):
    lst.append(val)
    return lst
```

**Ответ:** Используется изменяемый аргумент по умолчанию (*mutable default argument*). Список `lst` создаётся один раз и затем используется всеми вызовами функции.

Правильный вариант:

```python
def append_item(val, lst=None):
    if lst is None:
        lst = []
    lst.append(val)
    return lst
```

---

### 3. Что делает выражение `Path("data") / "file.csv"`?

**Ответ:** Создаёт путь к файлу, независимый от операционной системы. Это аналог:

```python
os.path.join("data", "file.csv")
```

но более читаемый и объектно-ориентированный способ работы с путями.

---

### 4. В чём разница между `json.dump()` и `json.dumps()`?

**Ответ:**

* `json.dump()` записывает JSON непосредственно в файловый объект.
* `json.dumps()` возвращает JSON в виде строки.

Пример:

```python
import json

with open("data.json", "w") as f:
    json.dump(data, f)
```

```python
import json

json_string = json.dumps(data)
```

---

### 5. Почему стоит использовать `csv.DictReader` вместо `csv.reader`?

**Ответ:** `DictReader` преобразует каждую строку CSV в словарь, где ключами являются названия столбцов. Это делает код более понятным, самодокументируемым и устойчивым к изменению порядка столбцов.

Пример:

```python
from csv import DictReader

with open("users.csv") as f:
    reader = DictReader(f)

    for row in reader:
        print(row["name"])
```

Вместо:

```python
from csv import reader

with open("users.csv") as f:
    csv_reader = reader(f)

    for row in csv_reader:
        print(row[0])
```
