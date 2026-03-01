# src/api/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src.db.database import get_db
from src.db.models import User
from src.api import auth, schemas
from src.api.routes import prices

# ─────────────────────────────────────────────────────────────
# Инициализация приложения
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="🥕 AgroPrice API",
    description="API для мониторинга цен на овощи и фрукты",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─────────────────────────────────────────────────────────────
# Регистрация роутов
# ─────────────────────────────────────────────────────────────
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])


# ─────────────────────────────────────────────────────────────
# Эндпоинты авторизации
# ─────────────────────────────────────────────────────────────
@app.post("/api/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Получить JWT токен (OAuth2 совместимый)"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/register", response_model=schemas.UserResponse)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверка: не занят ли username/email
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username уже занят")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Создаём пользователя
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=auth.get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ─────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "service": "AgroPrice API"}