# test_db_connection.py
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"✅ Успешное подключение к PostgreSQL!")
        print(f"📦 Версия БД: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
