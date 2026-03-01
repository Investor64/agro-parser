# run_parser.py
from sqlalchemy import func, cast, Date
from datetime import datetime, date
from sqlalchemy.orm import Session
from loguru import logger
from src.db.database import SessionLocal
from src.db.models import PriceRecord
from src.parsers.mock_parser import MockParser  # ← Изменено


def save_to_database(records: list, db: Session):
    """Сохранить записи в базу данных с дедупликацией"""
    saved_count = 0
    skipped_count = 0
    
    for record in records:
        existing = db.query(PriceRecord).filter(
            PriceRecord.product == record['product'],
            PriceRecord.source == record['source'],
            cast(PriceRecord.collected_at, Date) == date.today()).first()
        
        if existing:
            skipped_count += 1
            continue
        
        new_record = PriceRecord(
            product=record['product'],
            category='овощи' if record['product'] in ['лук', 'чеснок', 'морковь', 'картофель', 'помидоры', 'огурцы'] else 'фрукты',
            price=record['price'],
            currency=record['currency'],
            unit=record['unit'],
            source=record['source'],
            region=record['region']
        )
        
        db.add(new_record)
        saved_count += 1
    
    db.commit()
    logger.info(f"💾 Сохранено: {saved_count}, Пропущено (дубликаты): {skipped_count}")
    return saved_count


def main():
    """Основная функция запуска парсера"""
    logger.info("🚀 Запуск парсера цен...")
    
    parser = MockParser()  # ← Изменено
    
    records = parser.parse_all()
    
    if not records:
        logger.warning("⚠️ Данные не собраны!")
        return
    
    db = SessionLocal()
    try:
        saved = save_to_database(records, db)
        logger.success(f"✅ Парсинг завершён! Сохранено {saved} записей")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()