# src/api/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ─────────────────────────────────────────────────────────────
# Пользователи
# ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Цены
# ─────────────────────────────────────────────────────────────
class PriceRecordCreate(BaseModel):
    product: str
    price: float
    currency: Optional[str] = "RUB"
    unit: Optional[str] = "kg"
    source: Optional[str] = None
    region: Optional[str] = "Краснодарский край"


class PriceRecordResponse(BaseModel):
    id: int
    product: str
    category: Optional[str]
    price: float
    currency: str
    unit: str
    source: Optional[str]
    region: Optional[str]
    collected_at: datetime
    
    class Config:
        from_attributes = True


class PriceStats(BaseModel):
    product: str
    current_price: float
    avg_price: float
    min_price: float
    max_price: float
    change_percent: Optional[float]