# src/api/routes/prices.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

# Импортируем модели
from src.db.models import PriceRecord, User
from src.db.database import get_db
from src.api import schemas, auth

router = APIRouter()


@router.get("/", response_model=List[schemas.PriceRecordResponse])
def get_prices(
    product: Optional[str] = Query(None, description="Фильтр по товару"),
    source: Optional[str] = Query(None, description="Фильтр по источнику"),
    days: int = Query(30, ge=1, le=365, description="Период в днях"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Получить список цен (требуется авторизация)"""
    query = db.query(PriceRecord)
    
    if product:
        query = query.filter(PriceRecord.product.ilike(f"%{product}%"))
    if source:
        query = query.filter(PriceRecord.source == source)
    
    date_from = datetime.now() - timedelta(days=days)
    query = query.filter(PriceRecord.collected_at >= date_from)
    
    return query.order_by(PriceRecord.collected_at.desc()).limit(100).all()


@router.get("/stats/{product}", response_model=schemas.PriceStats)
def get_price_stats(
    product: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Получить статистику по товару"""
    date_from = datetime.now() - timedelta(days=days)
    
    records = db.query(PriceRecord).filter(
        PriceRecord.product.ilike(f"%{product}%"),
        PriceRecord.collected_at >= date_from
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    
    prices = [r.price for r in records]
    current = prices[-1] if prices else 0
    first = prices[0] if prices else 0
    
    return schemas.PriceStats(
        product=product,
        current_price=current,
        avg_price=sum(prices) / len(prices),
        min_price=min(prices),
        max_price=max(prices),
        change_percent=((current / first) - 1) * 100 if first else None
    )