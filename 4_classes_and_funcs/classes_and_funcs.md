# Глава 4 - Продвинутый Python: синтаксический сахар, типизация, парадигмы программирования

## Часть 1. Синтаксический сахар (II)

### 1.1 Walrus-оператор `:=` (Python 3.8+)

| Обычное присваивание (`=`) | Walrus-оператор (`:=`) |
|----------------------------|-------------------------|
| **Отдельная строка**<br>`x = 10`<br>`print(x)` | **Присваивание внутри выражения**<br>`(y := 10)   # и присвоили, и значение получили`<br>`print(y)     # y уже существует` |
| **Сначала вычислили, потом проверили**<br>`n = len(data)`<br>`if n > 0:`<br>`    print(n)` | **Вычислили И сохранили в одном месте**<br>`if (n := len(data)) > 0:`<br>`    print(f"Есть {n} элементов")` |
| **В циклах - чтение и проверка**<br>`line = file.readline()`<br>`while line != '':`<br>`    process(line)`<br>`    line = file.readline()` | **Чтение и проверка в заголовке while**<br>`while (line := file.readline()) != '':`<br>`    process(line)`<br>`    # line обновляется автомагически` |
| **Не работает внутри**<br>• f-строк<br>• comprehensions (кроме условия) | **Везде, где ждут выражение**<br>`[res for x in data if (res := func(x)) > 0]` |
| Разделение вычисления<br>и использования | Слияние вычисления<br>и использования |

**Когда полезно:** циклы `while`, list comprehension с промежуточным вычислением, чтобы не вызывать функцию дважды.

### 1.2 Тернарный оператор

Синтаксис:
значение_если_да if условие else значение_если_нет

Присваивание в одну строку, заменяет if-else из двух веток.
Цепочка условий в одной строке, заменяет if-elif-else.

**Вложенные выражения рекомендуется использовать осторожно - читаемость резко падает.**

### 1.3 Распаковка (unpacking)

Множественное присваивание:

1. Параллельное присваивание:
   Слева - кортеж переменных, справа - итерируемый объект.
   Количество должно совпадать.

2. Расширенная распаковка с астериском (*):
   *захватывает произвольное количество элементов в список.
   Может стоять в начале, середине или конце:
   - first, *rest = iterable       - первый + всё остальное списком
   - *init, last = iterable        - всё кроме последнего списком + последний
   - first, *middle, last = iterable - первый, середина списком, последний

3. Распаковка в вызовах функций:
   func(*args) - звёздочка разворачивает итерируемый объект в позиционные аргументы.

4. Слияние словарей через **:
   {**dict1, **dict2} - создаёт новый словарь, объединяя ключи.
   Если ключи повторяются, побеждает последний (правый).
   Удобно для создания копии с изменёнными полями.

### 1.4 `*args` и `**kwargs`

**Как это работает:**

1. **`*args`** (с одним астериском) - собирает все переданные позиционные аргументы в **кортеж** `args`.

2. **`**kwargs`** (с двумя астерисками) - собирает все переданные именованные аргументы в **словарь** `kwargs`.

**Имена `args` и `kwargs` - соглашение.** Синтаксически важны только астериски: можно писать `*items`, `**config` и т.д., но `args` и `kwargs` - общепринятый стандарт.

**Внутри функции:**
- `args` - это обычный кортеж, можно итерировать, обращаться по индексу.
- `kwargs` - это обычный словарь, можно использовать `.get()`, `.items()` и т.д.

Используется повсеместно в декораторах, обёртках API, ORM-моделях - везде, где нужно прокинуть произвольные аргументы дальше.

### 1.5 `zip` и `enumerate`

**`zip`** - объединяет несколько итерируемых объектов поэлементно в кортежи.

**`enumerate`** - оборачивает итерируемый объект и выдаёт пары (индекс, элемент).
Индекс по умолчанию с нуля, параметр `start` сдвигает начало отсчёта.

**Совместное использование `enumerate(zip(...))`:**

- `zip(names, scores)` даёт пары: `("Аня", 85)`, `("Борис", 92)`, `("Вера", 78)`
- `enumerate(..., start=1)` добавляет нумерацию с единицы: `(1, ("Аня", 85))`, ...


**`zip(*matrix)` для транспонирования:**

- `*matrix` распаковывает матрицу - строки становятся отдельными аргументами: `zip([1,2,3], [4,5,6])`
- `zip` берёт элементы с одинаковыми индексами: первые элементы строк `(1,4)`, вторые `(2,5)`, третьи `(3,6)`
- Строки превращаются в столбцы - готовая транспонированная матрица.

matrix = [[1, 2, 3], [4, 5, 6]]

list(zip(matrix))
→ [([1, 2, 3],), ([4, 5, 6],)]
  zip получает 1 аргумент - список matrix целиком.
  Каждый элемент matrix (то есть целая строка) упаковывается в кортеж из одного элемента.

list(zip(*matrix))
→ [(1, 4), (2, 5), (3, 6)]
  *matrix распаковывает matrix в 2 отдельных аргумента: [1,2,3] и [4,5,6].
  zip получает 2 аргумента и объединяет их поэлементно:
  первые элементы → (1, 4), вторые → (2, 5), третьи → (3, 6).

### 1.6 Продвинутые f-strings

_Базовые операторы форматирования в f-строках:_

{var} - вставка значения переменной.
{var=} - отладочный вывод с именем переменной (Python 3.8+).
{var:spec} - форматирование, где spec это: .2f (число с плавающей точкой, два знака после запятой), .2e (экспоненциальная форма), , (разделитель тысяч запятой), >10 (выравнивание по правому, ширина 10), <10 (по левому), ^10 (по центру). Можно комбинировать: {value:>10,.2f} - ширина 10, запятые, два знака после запятой, выравнивание вправо.

### 1.7 Декораторы

Декоратор — это функция, которая принимает одну функцию и возвращает другую, добавляя поведение до/после вызова.

_Простой декоратор:_

def timer(func):                  # 1. Принимает функцию, которую декорируем
    @functools.wraps(func)        # 2. Копирует метаданные (имя, докстринг) (опционально, больше нужно для разработчиков ПО на python)
    def wrapper(*args, **kwargs): # 3. Обёртка с любыми аргументами
        # ... код до вызова ...
        result = func(*args, **kwargs)  # 4. Вызов оригинальной функции
        # ... код после вызова ...
        return result             # 5. Возвращает результат оригинальной функции
    return wrapper                # 6. Возвращает обёртку вместо оригинальной функции

@timer                            # синтаксический сахар
def slow_sum(n): ...              # эквивалентно: slow_sum = timer(slow_sum)

Что делает @functools.wraps:
- Копирует __name__, __doc__, __module__ из func в wrapper
- Без него slow_sum.__name__ покажет "wrapper" вместо "slow_sum"

_Декоратор с параметрами:_

def retry(times=3):               # 1. Внешняя функция — принимает параметры декоратора
    def decorator(func):          # 2. Средняя функция — сам декоратор
        @functools.wraps(func)
        def wrapper(*args, **kwargs): # 3. Обёртка с логикой
            # использует times из замыкания
        return wrapper
    return decorator              # 4. Возвращает декоратор

@retry(times=5)                   # Сначала retry(times=5) вызывается,
def fetch(): ...                  # возвращает decorator,
                                  # потом decorator(fetch) заменяет функцию.
                                  # Эквивалентно: fetch = retry(times=5)(fetch)

Ключевое различие:
- @decorator       — decorator — это сам декоратор (принимает функцию)
- @decorator(...)  — decorator(...) вызывается и возвращает декоратор (принимает функцию)

=========================================================================================================================================
**HERE**
=========================================================================================================================================

## Часть 2. Типизация (25–45 мин)

Python - язык с динамической типизацией, но модуль `typing` даёт статические подсказки типов, которые проверяются внешними инструментами (не интерпретатором!).

### 2.1 Базовые аннотации

```python
def greet(name: str, age: int = 18) -> str:
    return f"{name}, {age} лет"

numbers: list[int] = [1, 2, 3]
mapping: dict[str, float] = {"eur": 1.1, "usd": 1.0}
```

> В Python 3.9+ можно писать `list[int]`, `dict[str, int]` напрямую, без импорта `List`/`Dict` из `typing`.

### 2.2 `Optional`, `Union` и `|`

```python
from typing import Optional, Union

def find_user(user_id: int) -> Optional[dict]:
    # Optional[dict] == Union[dict, None]
    ...

def parse(value: Union[str, int]) -> float:
    ...

# Python 3.10+: короткий синтаксис
def parse_new(value: str | int) -> float:
    ...

def find_user_new(user_id: int) -> dict | None:
    ...
```

### 2.3 `Literal`

Ограничивает значение конкретным набором вариантов - полезно для флагов и режимов.

```python
from typing import Literal

def set_mode(mode: Literal["train", "eval", "predict"]) -> None:
    ...

set_mode("train")     # ок
set_mode("debug")     # mypy подсветит ошибку
```

### 2.4 `@dataclass` - замена "словарей с данными"

Частая ошибка в аналитическом коде - таскать данные в "голых" словарях (`{"name": ..., "value": ...}`), где легко опечататься в ключе и получить `KeyError` в рантайме. `dataclass` решает это через явную структуру.

```python
from dataclasses import dataclass, field

@dataclass
class Transaction:
    id: int
    category: str
    amount: float
    tags: list[str] = field(default_factory=list)

t = Transaction(id=1, category="еда", amount=450.0)
print(t)                     # автоматический __repr__
print(t.amount)               # обращение через атрибут, не через ["amount"]
```

`@dataclass` бесплатно генерирует `__init__`, `__repr__`, `__eq__`. Сравните со словарём:

```python
# Словарь: опечатка в ключе - ошибка только в рантайме
tx = {"categoty": "еда", "amount": 450.0}   # опечатка не будет замечена статически

# Dataclass: опечатка в поле - mypy/IDE подсветят сразу
tx = Transaction(categoty="еда", amount=450.0)   # ошибка обнаружена до запуска
```

### 2.5 Базовые `Protocol` и `Generic`

`Protocol` - "утиная типизация" со статической проверкой: объект подходит под тип, если у него есть нужные методы, без явного наследования.

```python
from typing import Protocol

class Reporter(Protocol):
    def report(self) -> str: ...

def print_report(obj: Reporter) -> None:
    print(obj.report())

# Любой класс с методом report() подходит - не нужно наследоваться от Reporter
class SalesSummary:
    def report(self) -> str:
        return "Отчёт по продажам"

print_report(SalesSummary())   # ок для mypy
```

`Generic` - типизированные контейнеры/классы, параметризуемые типом:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

int_stack: Stack[int] = Stack()
int_stack.push(5)
```

### 2.6 Зачем `mypy` в команде

- Типы - это **исполняемая документация**: не нужно лезть в реализацию функции, чтобы понять, что она принимает и возвращает.
- Статический анализатор (`mypy`, `pyright`) ловит ошибки типов **до** запуска кода - особенно ценно в пайплайнах данных, где ошибка вылезает через час обработки.
- Упрощает ревью кода и рефакторинг больших кодовых баз.
- **Важно проговорить:** аннотации типов в Python - это подсказки, интерпретатор их не проверяет. Проверка - задача отдельного инструмента (`mypy`), который обычно встраивают в CI.

---

## Часть 3. Парадигмы программирования (45–70 мин)

Одну и ту же задачу можно решить разными "стилями мышления". Разберём три классических подхода на одном примере.

**Задача:** посчитать суммарные продажи по категориям из списка транзакций.

```python
transactions = [
    {"category": "еда", "amount": 450.0},
    {"category": "транспорт", "amount": 120.0},
    {"category": "еда", "amount": 300.0},
    {"category": "развлечения", "amount": 900.0},
    {"category": "транспорт", "amount": 80.0},
]
```

### 3.1 Процедурный стиль

```python
totals = {}
for tx in transactions:
    category = tx["category"]
    amount = tx["amount"]
    if category not in totals:
        totals[category] = 0.0
    totals[category] += amount

print(totals)
```

Прямолинейно, легко читается новичком, но: изменяемое состояние (`totals`) собирается вручную, легко забыть проверку `if category not in totals`.

### 3.2 Функциональный стиль

```python
from functools import reduce
from collections import defaultdict

# Вариант через reduce
def accumulate(acc: dict, tx: dict) -> dict:
    acc[tx["category"]] = acc.get(tx["category"], 0.0) + tx["amount"]
    return acc

totals = reduce(accumulate, transactions, {})

# Более "питонический" функциональный вариант - через defaultdict + comprehension
totals = defaultdict(float)
for category, amount in ((tx["category"], tx["amount"]) for tx in transactions):
    totals[category] += amount
```

Акцент на *чистых функциях* (без побочных эффектов) и неизменяемости данных на входе. `map`/`filter` пригодились бы, например, для предварительной фильтрации:

```python
big_transactions = list(filter(lambda tx: tx["amount"] > 200, transactions))
amounts = list(map(lambda tx: tx["amount"], transactions))
```

### 3.3 Объектно-ориентированный стиль

```python
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Transaction:
    category: str
    amount: float

class SalesAggregator:
    def __init__(self) -> None:
        self._totals: dict[str, float] = defaultdict(float)

    def add(self, transaction: Transaction) -> None:
        self._totals[transaction.category] += transaction.amount

    def as_dict(self) -> dict[str, float]:
        return dict(self._totals)

    def __repr__(self) -> str:
        return f"SalesAggregator({self.as_dict()})"

aggregator = SalesAggregator()
for tx in transactions:
    aggregator.add(Transaction(**tx))

print(aggregator)
```

Здесь состояние инкапсулировано внутри объекта, а не "болтается" в глобальной переменной. Легко расширить: добавить метод `top_category()`, `reset()`, логирование и т.д. без изменения внешнего интерфейса.

### 3.4 ООП: наследование vs композиция

```python
# Наследование - "является" (is-a)
class BaseAggregator:
    def __init__(self):
        self._totals = defaultdict(float)

    def add(self, category: str, amount: float) -> None:
        self._totals[category] += amount

class WeightedAggregator(BaseAggregator):
    def add(self, category: str, amount: float, weight: float = 1.0) -> None:
        self._totals[category] += amount * weight

# Композиция - "содержит" (has-a), обычно гибче
class ReportBuilder:
    def __init__(self, aggregator: BaseAggregator) -> None:
        self._aggregator = aggregator   # используем через композицию, не наследуемся

    def build(self) -> str:
        return "\n".join(f"{k}: {v:.2f}" for k, v in self._aggregator._totals.items())
```

**Практическое правило:** "composition over inheritance" - наследование создаёт жёсткую связь между классами и легко приводит к хрупким иерархиям при росте требований; композиция даёт гибкость и упрощает тестирование.

### 3.5 Dunder-методы

```python
class Money:
    def __init__(self, amount: float, currency: str = "RUB"):
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать разные валюты")
        return Money(self.amount + other.amount, self.currency)

a = Money(100)
b = Money(50)
print(a + b)          # Money(150, 'RUB')
print(a == Money(100))  # True
```

### 3.6 Метаклассы: как Python создаёт сами классы

До сих пор мы писали *классы*, которые создают *объекты*. Метаклассы отвечают на следующий вопрос: а кто создаёт сами классы? Это продвинутая тема, но она снимает "магию" с многих библиотек (Django ORM, Pydantic, ABC, dataclasses изнутри) и часто встречается на собеседованиях на позиции с Python.

**Ключевой факт:** в Python классы - это тоже объекты, и у них тоже есть тип.

```python
class SalesAggregator:
    pass

print(type(SalesAggregator))        # <class 'type'>
print(type(SalesAggregator()))      # <class '__main__.SalesAggregator'>
```

`type` - это метакласс по умолчанию: он "штампует" все классы, которые мы объявляем через `class`. Более того, `type` можно вызвать напрямую, без ключевого слова `class`:

```python
# Эквивалентные способы создать класс
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

Point = type("Point", (), {"__init__": lambda self, x, y: (setattr(self, "x", x), setattr(self, "y", y))})
```

**Свой метакласс** - это класс, унаследованный от `type`, который переопределяет, как создаются классы (не экземпляры классов, а сами классы):

```python
class LoggingMeta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"Создаётся класс: {name}")
        return super().__new__(mcs, name, bases, namespace)

class Report(metaclass=LoggingMeta):
    pass
# При импорте модуля выведет: "Создаётся класс: Report"
```

**Зачем это нужно на практике** (а не просто "потому что можно"):

```python
# 1. Автоматическая регистрация подклассов - паттерн "плагины"
class PluginMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # не регистрируем базовый класс
            mcs.registry[name] = cls
        return cls

class BaseExporter(metaclass=PluginMeta):
    pass

class CSVExporter(BaseExporter):
    pass

class JSONExporter(BaseExporter):
    pass

print(PluginMeta.registry)   # {'CSVExporter': <class ...>, 'JSONExporter': <class ...>}


# 2. Валидация структуры класса на этапе объявления (в духе ORM/Pydantic)
class RequiresFieldsMeta(type):
    def __new__(mcs, name, bases, namespace):
        if bases and "validate" not in namespace:
            raise TypeError(f"{name} должен реализовать метод validate()")
        return super().__new__(mcs, name, bases, namespace)


# 3. Синглтон на уровне метакласса
class SingletonMeta(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.settings = {}

a = ConfigManager()
b = ConfigManager()
print(a is b)   # True - один и тот же объект
```

**Важная оговорка для магистрантов:** метаклассы - мощный, но редко необходимый инструмент. Как говорил Тим Питерс: *"Metaclasses are deeper magic than 99% of users should ever worry about"*. Прежде чем писать свой метакласс, стоит проверить более простые альтернативы:

```python
# __init_subclass__ (Python 3.6+) - решает многие задачи без метакласса
class BasePlugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePlugin.registry[cls.__name__] = cls

class CSVPlugin(BasePlugin):
    pass

print(BasePlugin.registry)   # {'CSVPlugin': <class ...>} - без единого метакласса
```

| Задача | Метакласс нужен? | Альтернатива |
|---|---|---|
| Регистрация подклассов | Обычно нет | `__init_subclass__` |
| Валидация атрибутов класса при определении | Обычно нет | `__init_subclass__`, декоратор класса |
| Изменение поведения создания экземпляра (синглтон, кеш) | Иногда | `__new__` в самом классе, фабричная функция |
| ORM-подобное поведение полей (Django Model, Pydantic BaseModel) | Да, это классический сценарий | - |
| Библиотечный код, где нужен контроль над иерархией классов третьих сторон | Да | - |

**Практическое правило:** если сомневаетесь, нужен ли метакласс - скорее всего, не нужен. Метаклассы оправданы в первую очередь при написании библиотек/фреймворков, а не прикладного аналитического кода.

### 3.7 Обсуждение: что выбрать?

| Критерий | Процедурный | Функциональный | ООП |
|---|---|---|---|
| Порог входа | Низкий | Средний | Средний-высокий |
| Тестируемость | Средняя | Высокая (чистые функции) | Высокая (изоляция состояния) |
| Расширяемость при росте требований | Низкая | Средняя | Высокая |
| Типичное применение | Скрипты, разовые расчёты | Пайплайны трансформации данных | Долгоживущие системы, домены с состоянием |
| Риски | "Спагетти"-код при росте | Плохая читаемость при избыточной вложенности | Излишняя абстракция для простых задач |

**Ключевая мысль для студентов:** парадигма - это инструмент, а не религия. В одном модуле нормально сочетать функциональные трансформации данных (`pandas`, comprehensions) с объектной инкапсуляцией бизнес-логики.

---

## Часть 4. Исключения и контекстные менеджеры (70–85 мин)

### 4.1 `try / except / else / finally`

```python
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Файл {path} не найден, используем значения по умолчанию")
        return {}
    except PermissionError as e:
        print(f"Нет доступа: {e}")
        raise
    else:
        # выполняется, только если исключений не было
        print("Файл успешно прочитан")
        return parse(data)
    finally:
        # выполняется всегда - используется для очистки ресурсов
        print("Попытка чтения конфигурации завершена")
```

### 4.2 Кастомные исключения

```python
class DataValidationError(Exception):
    """Базовое исключение для ошибок валидации данных."""

class MissingColumnError(DataValidationError):
    def __init__(self, column: str):
        self.column = column
        super().__init__(f"Отсутствует обязательная колонка: {column}")

def validate(df_columns: set[str]) -> None:
    required = {"category", "amount"}
    missing = required - df_columns
    if missing:
        raise MissingColumnError(missing.pop())

try:
    validate({"category"})
except MissingColumnError as e:
    print(f"Ошибка валидации: {e}, колонка: {e.column}")
```

Собственная иерархия исключений позволяет вызывающему коду ловить как конкретную ошибку, так и целую категорию (`except DataValidationError`).

### 4.3 `with` и протокол контекстного менеджера

```python
with open("data.csv") as f:
    content = f.read()
# файл гарантированно закрыт, даже если внутри блока было исключение
```

### 4.4 Собственный контекстный менеджер - через класс

```python
import time

class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self._start
        print(f"Блок выполнился за {elapsed:.4f} сек")
        return False   # False = не подавлять исключение, если оно было

with Timer():
    total = sum(range(10_000_000))
```

### 4.5 Собственный контекстный менеджер - через `contextlib.contextmanager`

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Блок выполнился за {elapsed:.4f} сек")

with timer():
    total = sum(range(10_000_000))
```

**Сравнение подходов:** класс - явный и удобен, когда нужно хранить состояние между `__enter__`/`__exit__` или переиспользовать логику через наследование. `contextmanager`-декоратор - короче для простых одноразовых случаев.

---

## Часть 5. Итоговая демонстрация (в рамках занятия)

Разбираем на экране все три реализации задачи "суммарные продажи по категориям" (процедурная / функциональная / ООП, см. Часть 3) бок о бок и обсуждаем:

1. Что произойдёт с каждым подходом, если требования изменятся: нужно добавить фильтрацию по дате, поддержку нескольких валют, кеширование результата?
2. Какой вариант проще покрыть unit-тестами?
3. Какой вариант проще прочитать человеку, который видит код впервые?

---

## Введение в домашнее задание (85–90 мин)

**Постановка задачи:** реализовать модуль обработки транзакций, который:

- использует `@dataclass` для представления транзакции с типизированными полями (`typing`, `Literal` для категории или статуса);
- предоставляет функциональную и объектно-ориентированную реализацию агрегации (на выбор студента - какую делать основной, какую альтернативной);
- обрабатывает некорректные данные через кастomные исключения;
- использует хотя бы один собственный контекстный менеджер (например, для логирования времени обработки или безопасной записи результата в файл);
- проходит проверку `mypy` без ошибок.

Детальное описание, критерии оценки и шаблон репозитория - в файле задания в LMS.

---

## Материалы и ресурсы

- [Документация модуля `typing`](https://docs.python.org/3/library/typing.html)
- [PEP 526 - Syntax for Variable Annotations](https://peps.python.org/pep-0526/)
- [PEP 572 - Assignment Expressions (walrus)](https://peps.python.org/pep-0572/)
- [Документация `dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [Документация `functools`](https://docs.python.org/3/library/functools.html)
- [Документация `contextlib`](https://docs.python.org/3/library/contextlib.html)
- [mypy - официальная документация](https://mypy.readthedocs.io/)
- [Python Data Model - официальная документация (метаклассы, `__new__`, протокол создания класса)](https://docs.python.org/3/reference/datamodel.html#metaclasses)
- Рекомендуемое чтение: *Fluent Python* (Luciano Ramalho), главы 7–9 (функции как объекты, декораторы, замыкания), 11 (протоколы и ABC), 24 (метаклассы и объекты классов)
- Рекомендуемое чтение: *Python Distilled* (David Beazley), глава 7 (классы и ООП)