**Задание:** Реализовать класс `TransactionProcessor` с:
- `@dataclass` для `Transaction`.
- Методом `process_batch(transactions)`, использующим выбранную вами парадигму.
- Декоратором `@retry(3)` на функции загрузки данных.
- Собственными исключениями для отсутствующих полей и некорректных сумм.

---

## Проверка понимания

1. Что делает `@functools.wraps(func)` внутри декоратора?
   > Копирует `__name__`, `__doc__` и другие атрибуты оригинальной функции в обёртку, чтобы при отладке и интроспекции был виден оригинальный объект, а не `wrapper`.

2. Каков вывод этого кода?
   ```python
   a, *b, c = [1, 2, 3, 4, 5]
   print(b)
   ```
   > `[2, 3, 4]`

3. Почему в `@dataclass` нужно использовать `field(default_factory=list)` вместо `tags: list = []`?
   > Изменяемое значение по умолчанию (`[]`) было бы общим для всех экземпляров (тот же баг, что и с изменяемыми аргументами функций по умолчанию). `default_factory` создаёт новый список для каждого экземпляра.

4. В чём разница между `else` и `finally` в блоке `try`?
   > `else` выполняется только если исключения не было; `finally` выполняется всегда — даже после исключения или `return`.

5. Какую парадигму (процедурную / функциональную / ООП) вы бы выбрали для одноразового исследовательского скрипта и почему?
   > Процедурную — проще всего написать быстро, удобно отлаживать, нет накладных расходов на классы или функциональную композицию.
**Задание:** Реализовать класс `TransactionProcessor` с:
- `@dataclass` для `Transaction`.
- Методом `process_batch(transactions)`, использующим выбранную вами парадигму.
- Декоратором `@retry(3)` на функции загрузки данных.
- Собственными исключениями для отсутствующих полей и некорректных сумм.

---

## Проверка понимания

1. Что делает `@functools.wraps(func)` внутри декоратора?
   > Копирует `__name__`, `__doc__` и другие атрибуты оригинальной функции в обёртку, чтобы при отладке и интроспекции был виден оригинальный объект, а не `wrapper`.

2. Каков вывод этого кода?
   ```python
   a, *b, c = [1, 2, 3, 4, 5]
   print(b)
   ```
   > `[2, 3, 4]`

3. Почему в `@dataclass` нужно использовать `field(default_factory=list)` вместо `tags: list = []`?
   > Изменяемое значение по умолчанию (`[]`) было бы общим для всех экземпляров (тот же баг, что и с изменяемыми аргументами функций по умолчанию). `default_factory` создаёт новый список для каждого экземпляра.

4. В чём разница между `else` и `finally` в блоке `try`?
   > `else` выполняется только если исключения не было; `finally` выполняется всегда — даже после исключения или `return`.

5. Какую парадигму (процедурную / функциональную / ООП) вы бы выбрали для одноразового исследовательского скрипта и почему?
   > Процедурную — проще всего написать быстро, удобно отлаживать, нет накладных расходов на классы или функциональную композицию.

#### `@dataclass` — структурированные данные без шаблонного кода
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Transaction:
    id: int
    category: str
    amount: float
    currency: str = "USD"
    tags: list[str] = field(default_factory=list)   # безопасное изменяемое значение по умолчанию
    note: Optional[str] = None

    @property
    def amount_eur(self) -> float:
        rates = {"USD": 0.92, "GBP": 1.15}
        return self.amount * rates.get(self.currency, 1.0)

t = Transaction(id=1, category="electronics", amount=500.0)
print(t)                 # Transaction(id=1, category='electronics', ...)
print(t.amount_eur)      # 460.0
print(t == Transaction(id=1, category="electronics", amount=500.0))  # True (авто __eq__)

@dataclass
class Transaction:
    id: int
    category: str
    amount: float
    currency: str = "USD"
    tags: list[str] = field(default_factory=list)   # безопасное изменяемое значение по умолчанию
    note: Optional[str] = None

    @property
    def amount_eur(self) -> float:
        rates = {"USD": 0.92, "GBP": 1.15}
        return self.amount * rates.get(self.currency, 1.0)

t = Transaction(id=1, category="electronics", amount=500.0)
print(t)                 # Transaction(id=1, category='electronics', ...)
print(t.amount_eur)      # 460.0
print(t == Transaction(id=1, category="electronics", amount=500.0))  # True (авто __eq__)