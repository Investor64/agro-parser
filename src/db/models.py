# src/db/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, UniqueConstraint, func
from sqlalchemy.sql import func
from .database import Base

# ─────────────────────────────────────────────────────────────
# Таблица пользователей (для авторизации в дашборде/API)
# ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<User {self.username}>"


# ─────────────────────────────────────────────────────────────
# Таблица цен (основные данные парсера)
# ─────────────────────────────────────────────────────────────
class PriceRecord(Base):
    __tablename__ = "price_records"
    
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String(100), index=True, nullable=False)
    category = Column(String(50), index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="RUB")
    unit = Column(String(10), default="kg")
    source = Column(String(50), index=True)
    region = Column(String(100), default="Краснодарский край")
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    

    
    def __repr__(self):
        return f"<PriceRecord {self.product}: {self.price} ₽/кг>"
