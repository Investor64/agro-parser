# 🥕 АгроЦены — Инструкция по запуску

## Шаг 1: Установка Docker
Скачайте с https://docker.com и установите

## Шаг 2: Запуск базы данных
```bash
docker compose up -d db

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Откройте .env и задайте пароль для БД

python create_tables.py

uvicorn src.api.main:app --host 0.0.0.0 --port 8000

streamlit run dashboard/app.py

Откройте: http://localhost:8501
Логин/пароль: создайте через API или попросите администратора


