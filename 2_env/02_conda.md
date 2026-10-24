# Установка Conda (Miniconda)

## Ubuntu

### Скачать

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

### Установить

```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

### Перезапустить терминал

```bash
source ~/.bashrc
```

### Проверить

```bash
conda --version
```

---

## macOS (Intel)

### Скачать

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
```

### Установить

```bash
bash Miniconda3-latest-MacOSX-x86_64.sh
```

### Перезапустить терминал

```bash
source ~/.zshrc
```

### Проверить

```bash
conda --version
```

---

## macOS (Apple Silicon M1/M2/M3)

### Скачать

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
```

### Установить

```bash
bash Miniconda3-latest-MacOSX-arm64.sh
```

### Перезапустить терминал

```bash
source ~/.zshrc
```

### Проверить

```bash
conda --version
```

---

## Windows 10

1. Скачать установщик:

https://repo.anaconda.com/miniconda/

2. Запустить `.exe` файл.

3. Нажать:

```text
Next → I Agree → Just Me → Install → Finish
```

4. Открыть **Anaconda Prompt**.

5. Проверить:

```cmd
conda --version
```

---

## Создать окружение

```bash
conda create -n myenv python=3.12
conda activate myenv
```
