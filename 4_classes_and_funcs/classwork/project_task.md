# Мини-проект: `orders_kit`

Небольшой пакет для анализа заказов из CSV. Только стандартные библиотеки, аннотации типов обязательны.

## Структура

```text
orders_kit/
├── pyproject.toml
├── README.md
├── src/
│   └── orders_kit/
│       ├── __init__.py
│       ├── core.py          # Order, load_orders, sum_by
│       └── decorators.py    # log_call
└── examples/
    ├── orders.csv
    └── basic_usage.py
```

## Что сделать

1. **`pyproject.toml`**: имя `orders_kit`, версия `0.1.0`, layout `src/`.
2. **`core.py`**:
   * класс `Order` (`order_id`, `amount`, `category`, `payment_type`) с `__repr__`;
   * `load_orders(path) -> list[Order]` через `csv.DictReader`;
   * `sum_by(orders, key) -> dict[str, float]` — сумма `amount` в разрезе поля (`"category"` или `"payment_type"`).
3. **`decorators.py`**: `@log_call` печатает вызов и результат; примените его к `sum_by`.
4. **`examples/basic_usage.py`**: загружает `orders.csv`, печатает суммы по категориям и по типу оплаты.
5. **`README.md`**: 3–5 строк — что это и как запустить.

## Проверка

```bash
pip install -e .
python examples/basic_usage.py
```
