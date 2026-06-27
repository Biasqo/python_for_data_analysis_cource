# Урок 1: Python: синтаксис и экосистема
**Введение**

1. Критерии оценок (домашние задания + экзамен)
2. План курса

---
## Начало
### Дорожная карта
#### Python
Python - интерпретируемый высокоуровневый язык программирования общего назначения с динамической типизацией и автоматическим управлением памятью.

#### Архитектурные особенности
* Интерпретируемый язык
* Динамическая типизация
* Автоматическое управление памятью
* Поддержка объектно-ориентированного, процедурного и  функционального программирования
* Кроссплатформенность
* Огромная экосистема сторонних библиотек и фреймворков
* Преимущества
* Высокая скорость разработки
* Лаконичный синтаксис позволяет писать меньше кода по сравнению с Java, C++ или C#.

#### Экосистема

Библиотеки для:

* AI/ML (TensorFlow, PyTorch)
* Data Science (Pandas, NumPy)
* Web (Django, FastAPI, Flask)
* Автоматизации и DevOps
* Простота поддержки

Код обычно легче читать и сопровождать, чем аналогичные проекты на более низкоуровневых языках.

#### Недостатки
* Низкая производительность
* Из-за интерпретации и динамической типизации Python существенно уступает C, C++, Rust и Go по скорости выполнения.
* GIL (Global Interpreter Lock)
* В CPython только один поток может исполнять байткод одновременно, что ограничивает эффективность многопоточности для CPU-intensive задач.
* Высокое потребление памяти
* Сложности масштабирования крупных проектов (нет типизации, сложно поддерживать многомодульность)

#### Работа с данными
  ```
  [Orchestration]
  Raw Data → NumPy → pandas / Polars → PySpark → Streamlit
  ```

| Библиотека/Фреймворк | Аналог | плюсы Python | Минусы Python |
|---|---|---|---|
| pandas | Excel pivot tables | Reproducibility, scale | Interactive exploration feel |
| PySpark | SQL-only ETL | Distributed scale | Local small datasets |
| Streamlit | Tableau / Power BI | Code-first dashboards | Enterprise governance |

---

#### Некоторые особенности языка
```python
import os
import sys
from pathlib import Path
import json
import csv

# Useful os / sys snippets
print(os.getcwd())              # current working directory
print(sys.version)              # Python version string
print(os.environ.get("HOME"))   # environment variable, safe get
```

#### pathlib — пути без хардкода
```python
from pathlib import Path

data_dir = Path("data")
file = data_dir / "transactions.csv"   # OS-agnostic path joining

print(file.exists())          # True/False
print(file.suffix)            # .csv
print(file.stem)              # transactions
print(file.parent)            # data

# Iterate all CSV files in a directory
for csv_file in data_dir.glob("*.csv"):
    print(csv_file.name)
```

#### Json - чтение и запись

Оператор `with` в Python упрощает управление ресурсами, автоматически выполняя операции инициализации и очистки. 
Он гарантирует корректное освобождение таких ресурсов, как файлы, подключения к базам данных и блокировки, даже если внутри блока возникает исключение.


```python
import json

# Write
summary = {"total": 15000, "currency": "USD", "count": 42}
with open("summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Read
with open("summary.json") as f:
    data = json.load(f)
print(data["total"])  # 15000
```

---

### ДЗ

**Задание:** Написать скрипт, который:
1. Читает `transactions.csv` с помощью `csv` модуля
2. Считает: total revenue, average transaction value, count per category.
3. Пишет a `summary.json` с результатами.

**Критерии:** правильный ответ, чистый код без хардкода

---

## Материалы

- Python docs: [pathlib](https://docs.python.org/3/library/pathlib.html), [csv](https://docs.python.org/3/library/csv.html), [json](https://docs.python.org/3/library/json.html)
- Documentation https://docs.python.org/3/