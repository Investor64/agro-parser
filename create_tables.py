# create_tables.py
from src.db.database import engine, Base
from src.db import models

def create_all_tables():
    """Создать все таблицы в базе данных"""
    print("📦 Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Список таблиц: {tables}")

if __name__ == "__main__":
    create_all_tables()
