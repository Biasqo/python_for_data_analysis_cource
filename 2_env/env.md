# Урок 2 — Виртуальные окружения: virtualenv и conda
**Блок 2 — Окружение Python**

---

### Зачем изолировать окружения?

**Ключевые проблемы, которые решает изоляция:**

| Проблема | Первопричина | Решение |
|---|---|---|
| «У меня работает» | Разные версии пакетов | Фиксируйте версии для каждого проекта |
| Повреждение системного Python | Некорректный глобальный `pip install` | Окружения для каждого проекта |
| Конфликты версий Python | Проект A требует 3.9, проект B — 3.11 | Окружения conda |
| Трудности с онбордингом | Нет воспроизводимой настройки | `requirements.txt` / `environment.yml` |

#### Создание и активация
```bash
# Создаём окружение в директории проекта
python -m venv .venv

# Активация (Linux/macOS)
source .venv/bin/activate

# Активация (Windows)
.venv\Scripts\activate

# Проверяем, что находимся внутри окружения
which python           # должно указывать на .venv/bin/python
python --version
```

#### Установка пакетов и фиксация версий
```bash
pip install pandas==2.1.0 numpy==1.26.0 requests

# Зафиксировать точные установленные версии
pip freeze > requirements.txt

# Установить из requirements на другой машине
pip install -r requirements.txt
```

#### Стратегии фиксации версий
```
# requirements.txt — точная фиксация (для production / воспроизводимости)
pandas==2.1.0
numpy==1.26.0

# requirements-dev.txt — диапазон (для библиотек, гибкость)
pandas>=2.0,<3.0
numpy>=1.25
```

**Когда использовать точную фиксацию:** общие репозитории с анализом, опубликованные результаты, CI-пайплайны.  
**Когда использовать диапазоны:** библиотеки, которые вы публикуете для других.

#### Деактивация
```bash
deactivate
```

---

#### Когда необходима conda
- Пакеты с нативными расширениями на C/Fortran (например, MKL-ускоренный NumPy, некоторые конфигурации PySpark).
- Необходимо управлять самой версией Python (не только пакетами).
- Стеки для data science / научных вычислений под Windows.

#### Основные команды
```bash
# Создать новое окружение
conda create -n course-env python=3.11

# Активировать
conda activate course-env

# Установить пакеты (предпочтителен канал conda-forge)
conda install -c conda-forge pandas numpy jupyterlab

# Смешанный вариант: conda для скомпилированных зависимостей, pip — для остального
conda install -c conda-forge numpy
pip install polars streamlit

# Экспорт
conda env export > environment.yml

# Воссоздать на другой машине
conda env create -f environment.yml
```

#### Структура environment.yml
```yaml
name: course-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy=1.26.0
  - pandas=2.1.0
  - pip:
    - polars==0.20.0
    - streamlit==1.30.0
```

#### conda vs pip — правило выбора
```
Нужно управлять самой версией Python?             → conda
Пакет содержит тяжёлый нативный код (C/Fortran)?  → conda (установить через conda-forge)
Чистый Python-пакет?                              → pip подойдёт
Смешанный стек (научный + веб)?                   → conda для базы + pip для остального
```

---

### Структура проекта

```
my_project/
├── .venv/                  # или conda-окружение (добавить в .gitignore)
├── data/
│   ├── raw/                # сырые файлы — никогда не изменять
│   └── processed/
├── notebooks/              # только для исследований
├── src/
│   └── my_project/         # импортируемый пакет
│       ├── __init__.py
│       └── utils.py
├── tests/
├── .env                    # секреты — НИКОГДА не коммитить
├── .gitignore
├── requirements.txt
└── README.md
```

#### Необходимые записи в .gitignore
```gitignore
# Окружения
.venv/
env/
__pycache__/
*.pyc
*.pyo
.ipynb_checkpoints/

# Секреты
.env
*.key
*.pem

# Данные (часто слишком велики для git)
data/raw/
data/processed/
*.parquet
*.csv
```

#### .env + python-dotenv
```bash
pip install python-dotenv
```

---

### Практика: параллельная настройка

**Задание:** Настроить учебный проект с одинаковыми зависимостями двумя способами.

```bash
# Часть A — venv
python -m venv .venv-pip
source .venv-pip/bin/activate
pip install pandas==2.1.0 numpy==1.26.0 polars==0.20.0
pip freeze > requirements.txt
deactivate

# Часть B — conda
conda create -n course-conda python=3.11 -y
conda activate course-conda
conda install -c conda-forge numpy=1.26.0 pandas=2.1.0 -y
pip install polars==0.20.0
conda env export > environment.yml
conda deactivate
```

**DEBUGGER**

**Вопросы для размышления:**
1. Какой подход показался быстрее? Почему?
2. Как вы поделитесь этим окружением с коллегой, у которого есть только pip?
3. Что произойдёт, если выполнить `pip install` внутри conda-окружения?

---

---

## Материалы и ресурсы

- [Документация venv](https://docs.python.org/3/library/venv.html)
- [Шпаргалка conda](https://docs.conda.io/projects/conda/en/stable/user-guide/cheatsheet.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Шаблон репозитория курса: `github.com/course/template` (предоставляет преподаватель)