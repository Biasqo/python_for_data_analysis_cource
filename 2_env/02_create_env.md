# Установка Python Virtual Environment (venv) и Jupyter Notebook

## Проверка Python
Проверьте, установлен ли Python:
```
python --version
```
```
python3 --version
```
Если Python не установлен, установите его с официального сайта:
https://www.python.org/downloads/
---
# Windows (PowerShell)

## 1. Создание проекта
```
mkdir my_project
cd my_project
```

## 2. Создание виртуального окружения
```
python -m venv .venv
```
## 3. Активация окружения
```
.venv\Scripts\Activate.ps1
```

## 4. Обновление pip
```
python -m pip install --upgrade pip
```

## 5. Установка зависимостей
```
pip install -r requirements.txt
```

## 6. Установка ядра Jupyter
```
python -m ipykernel install --user --name=my_project
```

## 7. Запуск Jupyter
```
jupyter notebook
```
Советую предварительно установить vscode или pycharm для удобной работы в IDE


## 8. Выход из окружения
```
deactivate
```
---

# Linux / macOS / Bash

## 1. Создание проекта
```
mkdir my_project
cd my_project
```

## 2. Создание виртуального окружения
```
python3 -m venv .venv
```

## 3. Активация окружения
```
source .venv/bin/activate
```

## 4. Обновление pip
```
python -m pip install --upgrade pip
```

## 5. Установка зависимостей
```
pip install -r requirements.txt
```

## 6. Установка ядра Jupyter
```
python -m ipykernel install --user --name=my_project
```

## 7. Запуск Jupyter
```
jupyter notebook
```
Советую предварительно установить vscode или pycharm для удобной работы в IDE


## 8. Выход из окружения

```bash
deactivate
```