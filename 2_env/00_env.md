# Глава 2 — Виртуальные окружения, Jupyter и организация проекта

## 1. Зачем изолировать окружения?

При установке модулей (библиотек) для Python без изоляции, все они попадают в одно глобальное пространство. 
Это быстро приводит к конфликтам версий пакетов.

**Best practice**
| Практика |
|-----------------------------------------------------------|
| Фиксируйте версии для каждого проекта                     |
| Создавайте независимое окружение для каждого проекта      |
| Управленяйте версиями через conda или pyenv               |
| Всегда считывайте `requirements.txt` / `environment.yml`  |

**Золотое правило:** 
Одно окружение на один проект. Без исключений.

## 2. Как устроен venv изнутри

`venv` — стандартная библиотека Python (с версии 3.3), не нужно ничего дополнительно устанавливать.

### Что происходит при создании окружения

```bash
python -m venv .venv
```

Python создаёт директорию `.venv/` с такой структурой:

```
.venv/
├── bin/               # (Scripts/ на Windows)
│   ├── python         # симлинк → системный Python
│   ├── python3
│   ├── pip
│   └── activate       # скрипт активации
├── lib/
│   └── python3.11/
│       └── site-packages/   # сюда устанавливаются пакеты
└── pyvenv.cfg         # метаданные окружения
```

Содержимое `pyvenv.cfg`:
```ini
home = /usr/bin          # откуда взят Python
include-system-site-packages = false
version = 3.11.4
```

### Что делает `activate`

Скрипт `activate` изменяет три переменные окружения:

```bash
VIRTUAL_ENV="/path/to/project/.venv"
PATH=".venv/bin:$PATH"      # ставит окружение первым в PATH
PS1="(.venv) $PS1"          # показывает имя в промпте
```

Это означает, что `python` и `pip` теперь будут искаться сначала в `.venv/bin/`.

### Как проверить, что вы внутри окружения

```bash
# Должно указывать на .venv, а не системный Python
which python
# /home/user/my_project/.venv/bin/python

# Переменная окружения
echo $VIRTUAL_ENV
# /home/user/my_project/.venv

# В Python
python -c "import sys; print(sys.prefix)"
```

## 3. virtualenv и рабочие приёмы с venv

### Создание и управление

```bash
# Создаём (Python стандартной библиотеки, рекомендуется называть .venv)
python -m venv .venv

# Активация
source .venv/bin/activate          # Linux / macOS
.venv\Scripts\activate             # Windows CMD
.venv\Scripts\Activate.ps1         # Windows PowerShell

# Деактивация
deactivate

# Удалить и пересоздать (просто удаляем директорию)
rm -rf .venv
python -m venv .venv
```

`.venv` — стандартное имя (его понимают VS Code, PyCharm, ruff, mypy). 
Используйте его везде.
Точка нужна для того, чтобы случайно не закоммитить эту объемную папку в git (для этого и есть `requirements.txt`)

### Установка пакетов и фиксация версий

```bash
# Установка пакетов
pip install pandas==2.1.0 numpy==1.26.0 requests

# Зафиксировать точные установленные версии
pip freeze > requirements.txt

# Установить из requirements на другой машине
pip install -r requirements.txt

# Обновить один пакет и перезаписать requirements
pip install --upgrade pandas
pip freeze > requirements.txt
```

### Стратегии фиксации версий

```
# requirements.txt — точная фиксация (для production / воспроизводимости)
pandas==2.1.0
numpy==1.26.0

# requirements-dev.txt — диапазон (для библиотек, гибкость)
pandas>=2.0,<3.0
numpy>=1.25

# Два файла: dev зависит от prod
# requirements-dev.txt
-r requirements.txt     # включает prod зависимости
pytest>=7.0
black>=23.0
```

**Когда точная фиксация:** общие репозитории с анализом, опубликованные результаты, CI-пайплайны.
**Когда диапазоны:** библиотеки, которые вы публикуете для других.

### Полезные флаги pip

```bash
# Не устанавливать зависимости (опасно, но иногда нужно)
pip install requests --no-deps

# Показать, что установлено и почему
pip show pandas

# Проверить на устаревшие пакеты
pip list --outdated

# Установить из git-репозитория
pip install git+https://github.com/user/repo.git

# Установить в режиме разработки (изменения сразу видны без переустановки)
pip install -e .
```

### virtualenv vs venv

`virtualenv` — сторонний пакет, предшественник `venv`. Устанавливается отдельно (`pip install virtualenv`), но имеет преимущества:

```bash
pip install virtualenv

# Можно указать конкретный интерпретатор
virtualenv -p python3.9 .venv

# Быстрее создаёт окружения (кеширует системные пакеты)
virtualenv --system-site-packages .venv  # наследует системные пакеты
```

**Рекомендация:** используйте стандартный `venv`, если нет специфических потребностей.

### .env + python-dotenv

```bash
pip install python-dotenv
```

Файл `.env` (никогда не коммитить!):
```env
DATABASE_URL=postgresql://user:password@localhost/mydb
API_KEY=sk-abc123
DEBUG=true
```

Использование в Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # загружает .env в переменные окружения

db_url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")

# С дефолтным значением
debug = os.getenv("DEBUG", "false").lower() == "true"
```

---

## 4. conda: когда и как

### Когда необходима conda

- Нужно управлять **самой версией Python** (не только пакетами).
- Пакеты с **нативными расширениями** (MKL-NumPy, GDAL, некоторые конфигурации PySpark, OpenCV).
- Работа на **Windows** с data-science стеком.
- Нужны **не-Python зависимости** (ffmpeg, gdal, cuda toolkit).

### Основные команды

```bash
# Создать новое окружение с конкретной версией Python
conda create -n course-env python=3.11

# Активировать
conda activate course-env

# Деактивировать
conda deactivate

# Список всех окружений
conda env list

# Удалить окружение
conda env remove -n course-env
```

### Установка пакетов

```bash
# Устанавливать из conda-forge (лучшее качество сборок)
conda install -c conda-forge pandas numpy jupyterlab

# Смешанный вариант: conda для скомпилированных зависимостей
conda install -c conda-forge numpy scipy
pip install polars streamlit       # pip для чисто Python пакетов

# Поиск пакета
conda search pandas

# Обновить все пакеты
conda update --all
```

> **Важно!!!** если в conda-окружении использовать pip, сначала устанавливайте conda-пакеты, потом pip. Обратный порядок может сломать окружение.

### Экспорт и воссоздание

```bash
# Экспорт (включая системные зависимости — не переносить между ОС!)
conda env export > environment.yml

# Кроссплатформенный экспорт
conda env export --from-history > environment.yml

# Воссоздать на другой машине
conda env create -f environment.yml

# Обновить существующее окружение из файла
conda env update -f environment.yml --prune
```

### Структура environment.yml

```yaml
name: course-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy=1.26.0
  - pandas=2.1.0
  - jupyterlab=4.0.0
  - pip:           # pip-зависимости в конце
    - polars==0.20.0
    - streamlit==1.30.0
```

### conda vs pip — правило выбора

```
Нужно управлять самой версией Python?             → conda
Пакет содержит тяжёлый нативный код (C/Fortran)?  → conda (установить через conda-forge)
Чистый Python-пакет?                              → pip подойдёт
Смешанный стек (научный + веб)?                   → conda для базы + pip для остального
Нет conda, нужна другая версия Python?            → pyenv + venv
```

---

## 5. Jupyter: настройка и практические советы

### Установка и запуск

```bash
# Внутри вашего venv или conda-окружения
pip install jupyterlab          # современный интерфейс (рекомендуется)
# или
pip install notebook            # классический интерфейс

# Запуск
jupyter lab                     # откроет браузер
jupyter lab --no-browser        # без открытия браузера
jupyter lab --port 8889         # другой порт, если 8888 занят
```

### Ключевая проблема: Jupyter и ваши окружения

Jupyter запускает ноутбуки в **ядрах (kernels)**. 
По умолчанию он использует тот Python, в котором установлен. 
Если Jupyter и ваш проект в разных окружениях — вы не найдете ваши пакеты (модули).

**Best practice:** 
 Устанавливайте модуль `ipykernel`, создавайте окружения (через `pip` например) и регистрируйте ядра отдельно.

```bash
# Активируйте ваше рабочее окружение
conda activate course-env
source .venv/bin/activate

# Установите ipykernel
pip install ipykernel

# Зарегистрируйте окружение как ядро Jupyter
python -m ipykernel install --user --name course-env --display-name "Python (course-env)"

# Теперь в Jupyter можно выбрать это ядро из меню Kernel
```

Список зарегистрированных ядер:
```bash
jupyter kernelspec list
```

Удалить ядро:
```bash
jupyter kernelspec remove course-env
```

### Настройка Jupyter

Создать конфигурационный файл:
```bash
jupyter lab --generate-config
# Создаст ~/.jupyter/jupyter_lab_config.py
```

Полезные настройки в `jupyter_lab_config.py`:
```python
# Открывать в конкретной директории
c.ServerApp.root_dir = '/home/user/projects'

# Не открывать браузер автоматически
c.ServerApp.open_browser = False

# Токен авторизации (для удалённого сервера)
c.ServerApp.token = 'my-secret-token'
```

### Расширения и плагины

```bash
# Оглавление
pip install jupyterlab-toc

# Форматирование кода в ноутбуках
pip install jupyterlab-code-formatter black isort

# Git-интеграция
pip install jupyterlab-git

# Переменные среды (удобный просмотр)
pip install lckr-jupyterlab-variableinspector
```

### Советы по работе в Jupyter

**Горячие клавиши (выучить обязательно):**

| Действие | Клавиши |
|---|---|
| Запустить ячейку + перейти к следующей | `Shift + Enter` |
| Запустить ячейку, остаться | `Ctrl + Enter` |
| Добавить ячейку ниже | `B` (в командном режиме) |
| Добавить ячейку выше | `A` |
| Удалить ячейку | `DD` |
| Переключить в Markdown | `M` |
| Переключить в код | `Y` |
| Командная палитра | `Ctrl + Shift + C` |
| Перезапустить ядро | `00` |

> Нажмите `Esc` для перехода в командный режим, `Enter` — обратно в режим редактирования.

**Магические команды (`%` и `%%`):**

```python
# Измерить время выполнения ячейки
%%time
df = pd.read_csv("big_file.csv")

# Измерить время конкретной строки
%timeit df["col"].sum()

# Показать все переменные
%whos

# Запустить bash-команду
%bash ls -la
!pip list   # альтернатива

# Автоматически перезагружать модули (очень полезно при разработке)
%load_ext autoreload
%autoreload 2

# Встроить matplotlib-графики
%matplotlib inline

# Интерактивные графики
%matplotlib widget
```

**Рекомендации по использованию ноутбуков:**

- Ноутбуки — для **исследований и презентаций**, не для production-кода.
- Держите ячейки маленькими (не захламляйте кодом).
- Регулярно делайте **Restart & Run All** — убедиться, что ноутбук воспроизводим.
- Выносите переиспользуемые функции в `.py` модули, импортируйте их.

---

## 6. Организация проекта

### Рекомендуемая структура

```
my_project/
├── .venv/                  # или conda-окружение — добавить в .gitignore
├── data/
│   ├── raw/                # исходные файлы — никогда не изменять
│   ├── processed/          # результаты обработки
│   └── external/           # данные из внешних источников
├── notebooks/
│   ├── 01_eda.ipynb        # исследования — нумеровать!
│   └── 02_modeling.ipynb
├── src/
│   └── my_project/         # импортируемый пакет
│       ├── __init__.py
│       ├── data.py         # функции загрузки данных
│       ├── features.py     # feature engineering
│       ├── models.py       # модели
│       └── utils.py        # утилиты
├── tests/
│   └── test_utils.py
├── .env                    # секреты — НИКОГДА не коммитить
├── .gitignore
├── requirements.txt
├── requirements-dev.txt    # pytest, black, mypy и т.д.
└── README.md
```

### Необходимые записи в .gitignore

```gitignore
# Окружения
.venv/
env/
venv/
__pycache__/
*.pyc
*.pyo
.ipynb_checkpoints/

# Секреты
.env
*.key
*.pem
.env.local

# Данные (часто слишком велики для git)
data/raw/
data/processed/
*.parquet
*.csv
*.xlsx

# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp
```

### README

```markdown
## Настройка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # заполните свои значения
```

## Структура

Описание папок и что где лежит.

## Шпаргалка

```bash
# venv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt
deactivate

# conda
conda create -n myenv python=3.11 && conda activate myenv
conda install -c conda-forge pandas numpy
conda env export > environment.yml
conda env create -f environment.yml

# Jupyter — зарегистрировать окружение как ядро
pip install ipykernel
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"
jupyter kernelspec list
```

## Материалы и ресурсы

- [Документация venv](https://docs.python.org/3/library/venv.html)
- [Шпаргалка conda](https://docs.conda.io/projects/conda/en/stable/user-guide/cheatsheet.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Документация Jupyter](https://jupyterlab.readthedocs.io/)
- [ipykernel — регистрация ядер](https://ipython.readthedocs.io/en/stable/install/kernel_install.html)