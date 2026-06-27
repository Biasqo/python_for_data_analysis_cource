#!/bin/bash

mkdir demo_project && cd demo_project
python -m venv .venv
source .venv/bin/activate
pip install pandas requests
pip freeze                         # показываем «сырой» вывод
pip freeze > requirements.txt
cat requirements.txt               # показываем файл фиксации
deactivate


conda create -n demo-conda python=3.11 pandas requests -y
conda activate demo-conda
conda env export > environment.yml
cat environment.yml  

# --- Демо python-dotenv ---
echo "API_KEY=supersecret" > .env
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Ключ загружен:', bool(os.getenv('API_KEY')))
"
conda deactivate