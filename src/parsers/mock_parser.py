# src/parsers/mock_parser.py
import random
from datetime import datetime
from loguru import logger

# Список товаров для мониторинга
TARGET_PRODUCTS = [
    "лук", "чеснок", "морковь", "картофель", 
    "клубника", "помидоры", "огурцы"
]

# Базовые цены (реалистичные для Краснодарского края)
BASE_PRICES = {
    "лук": 25.0,
    "чеснок": 85.0,
    "морковь": 30.0,
    "картофель": 35.0,
    "клубника": 150.0,
    "помидоры": 90.0,
    "огурцы": 60.0
}

TARGET_REGION = "Краснодарский край"


class MockParser:
    """Генератор тестовых данных для разработки"""
    
    def __init__(self):
        logger.info("🎭 MockParser инициализирован (тестовые данные)")
    
    def _generate_price(self, base_price: float) -> float:
        """Генерация цены с небольшим разбросом (±15%)"""
        variation = random.uniform(-0.15, 0.15)
        return round(base_price * (1 + variation), 2)
    
    def _generate_source(self) -> str:
        """Случайный источник данных"""
        return random.choice(["agroserver", "rosstat", "foodcity", "manual"])
    
    def parse_all(self, records_per_product: int = 3) -> list:
        """Генерация тестовых записей"""
        all_records = []
        
        logger.info(f"🚀 Генерация тестовых данных для {len(TARGET_PRODUCTS)} товаров...")
        
        for product in TARGET_PRODUCTS:
            base_price = BASE_PRICES.get(product, 50.0)
            
            for i in range(records_per_product):
                record = {
                    'product': product,
                    'price': self._generate_price(base_price),
                    'currency': 'RUB',
                    'unit': 'kg',
                    'source': self._generate_source(),
                    'region': TARGET_REGION
                }
                all_records.append(record)
        
        logger.info(f"📦 Сгенерировано записей: {len(all_records)}")
        return all_records


# ─────────────────────────────────────────────────────────────
# Тестовый запуск
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = MockParser()
    data = parser.parse_all()
    
    print(f"\n📊 Результаты:")
    for record in data[:10]:
        print(f"  {record['product']}: {record['price']} ₽/кг ({record['source']})")