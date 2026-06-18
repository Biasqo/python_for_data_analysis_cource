# Lesson 2 — Virtual Environments: virtualenv & conda
**Block 2 — Python Environment | Duration: 90 minutes | Level: Intermediate/Advanced**

---

## Learning Objectives

By the end of this lesson, students will be able to:
1. Explain why environment isolation matters and what "dependency hell" looks like in practice.
2. Create, activate, and pin dependencies using both `venv`/`pip` and `conda`.
3. Set up a reproducible project scaffold that they will reuse for the rest of the course.

---

## Minute-by-Minute Plan

### 0–15 | Why Isolate Environments?

**Goal:** Make the problem visceral before introducing the solution.

**Scenario to discuss:**
> You trained an ML model six months ago. A colleague runs your script today and gets a different result — not because of the data, but because `pandas` was upgraded from `1.5` to `2.0` and the `groupby` behavior changed silently.

**Core problems isolation solves:**

| Problem | Root cause | Solution |
|---|---|---|
| "Works on my machine" | Different package versions | Lock versions per project |
| System Python corruption | Global `pip install` gone wrong | Per-project environments |
| Python version conflicts | Project A needs 3.9, Project B needs 3.11 | conda environments |
| Onboarding friction | No reproducible setup | `requirements.txt` / `environment.yml` |

**Analogy:** A virtual environment is like a Docker container for your Python interpreter — lightweight, disposable, reproducible.

---

### 15–40 | `venv` and `pip`

#### Creating and activating
```bash
# Create environment in the project directory
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Confirm you're inside
which python           # should point to .venv/bin/python
python --version
```

#### Installing and freezing
```bash
pip install pandas==2.1.0 numpy==1.26.0 requests

# Freeze exact installed versions
pip freeze > requirements.txt

# Install from requirements on another machine
pip install -r requirements.txt
```

#### Version pinning strategies
```
# requirements.txt — exact pin (production/reproducibility)
pandas==2.1.0
numpy==1.26.0

# requirements-dev.txt — range (libraries, flexibility)
pandas>=2.0,<3.0
numpy>=1.25
```

**When to use exact pins:** shared analysis repos, published results, CI pipelines.  
**When to use ranges:** libraries you publish for others to install.

#### Deactivating
```bash
deactivate
```

---

### 40–65 | conda

#### When conda is necessary
- Packages with native C/Fortran extensions (e.g., MKL-accelerated NumPy, some PySpark setups).
- Need to manage Python version itself (not just packages).
- Data science / scientific computing stacks on Windows.

#### Core commands
```bash
# Create a new environment
conda create -n course-env python=3.11

# Activate
conda activate course-env

# Install packages (prefer conda-forge channel)
conda install -c conda-forge pandas numpy jupyterlab

# Mix: use conda for compiled deps, pip for the rest
conda install -c conda-forge numpy
pip install polars streamlit

# Export
conda env export > environment.yml

# Recreate on another machine
conda env create -f environment.yml
```

#### environment.yml structure
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

#### conda vs pip — decision rule
```
Need to manage Python version itself?      → conda
Package has heavy C/Fortran native code?   → conda (install via conda-forge)
Pure Python package?                       → pip is fine
Mixed stack (scientific + web)?            → conda for base + pip for extras
```

---

### 65–80 | Project Structure

**Goal:** Students leave with a scaffold they keep for the entire course.

```
my_project/
├── .venv/                  # or conda env (gitignored)
├── data/
│   ├── raw/                # never modify raw files
│   └── processed/
├── notebooks/              # exploration only
├── src/
│   └── my_project/         # importable package
│       ├── __init__.py
│       └── utils.py
├── tests/
├── .env                    # secrets — NEVER commit
├── .gitignore
├── requirements.txt
└── README.md
```

#### .gitignore essentials
```gitignore
# Environments
.venv/
env/
__pycache__/
*.pyc
*.pyo
.ipynb_checkpoints/

# Secrets
.env
*.key
*.pem

# Data (often too large for git)
data/raw/
data/processed/
*.parquet
*.csv
```

#### .env + python-dotenv
```bash
pip install python-dotenv
```

```python
# .env (never commit this)
DATABASE_URL=postgresql://user:password@localhost/mydb
API_KEY=sk-abc123

# src/my_project/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DB_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ["API_KEY"]
```

**Why not hardcode secrets?**
- Git history is permanent — even a deleted secret may be recoverable.
- Public repos expose secrets to the entire internet instantly.

---

### 80–90 | Lab: Side-by-Side Setup

**Students do this themselves while instructor circulates.**

**Task:** Set up the course project with the same dependencies using both tools.

```bash
# Part A — venv
python -m venv .venv-pip
source .venv-pip/bin/activate
pip install pandas==2.1.0 numpy==1.26.0 polars==0.20.0
pip freeze > requirements.txt
deactivate

# Part B — conda
conda create -n course-conda python=3.11 -y
conda activate course-conda
conda install -c conda-forge numpy=1.26.0 pandas=2.1.0 -y
pip install polars==0.20.0
conda env export > environment.yml
conda deactivate
```

**Reflection questions:**
1. Which approach felt faster? Why?
2. How would you share this environment with a colleague who only has pip?
3. What happens if you `pip install` inside a conda environment?

---

## Live Demo Script

```bash
# Instructor runs this live, narrating each step

# --- venv demo ---
mkdir demo_project && cd demo_project
python -m venv .venv
source .venv/bin/activate
pip install pandas requests
pip freeze                         # show messy output
pip freeze > requirements.txt
cat requirements.txt               # show the pin file
deactivate

# --- conda demo ---
conda create -n demo-conda python=3.11 pandas requests -y
conda activate demo-conda
conda env export > environment.yml
cat environment.yml                # compare structure to requirements.txt

# --- python-dotenv demo ---
echo "API_KEY=supersecret" > .env
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Key loaded:', bool(os.getenv('API_KEY')))
"
conda deactivate
```

---

## Check for Understanding

**Exit ticket — 4 questions (answered on paper/chat at minute 88):**

1. Your colleague sends you `environment.yml`. What single command recreates their environment?
   > `conda env create -f environment.yml`

2. Why should `.env` be in `.gitignore`?
   > It contains secrets (API keys, passwords). Git history is permanent; once pushed, secrets are compromised.

3. What is wrong with this `requirements.txt`?
   ```
   pandas
   numpy
   ```
   > No version pins. Another developer (or future you) will get whatever the latest version is, which may behave differently. Use `pandas==2.1.0` etc.

4. When would you choose conda over venv?
   > When you need to manage the Python version itself, when packages require compiled native extensions (e.g., MKL NumPy), or on Windows where building C extensions with pip is painful.

---

## Materials & Resources

- [venv docs](https://docs.python.org/3/library/venv.html)
- [conda cheatsheet](https://docs.conda.io/projects/conda/en/stable/user-guide/cheatsheet.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Course repo template: `github.com/course/template` (provided by instructor)