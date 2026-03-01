# src/parsers/agroserver.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from loguru import logger
import time
import random

# Список товаров для мониторинга
TARGET_PRODUCTS = [
    "лук", "чеснок", "морковь", "картофель", 
    "клубника", "помидоры", "огурцы"
]

# Регион поиска
TARGET_REGION = "Краснодарский край"


class AgroserverParser:
    """Парсер цен с Agroserver.ru"""
    
    def __init__(self):
        self.base_url = "https://www.agroserver.ru"
        self.ua = UserAgent()
        self.session = requests.Session()
        logger.info("🕷 AgroserverParser инициализирован")
    
    def _get_headers(self) -> dict:
        """Получить заголовки для запроса"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    
    def _search_products(self, product: str) -> list:
        """Поиск товаров по названию"""
        results = []
        
        # Формируем URL поиска
        search_url = f"{self.base_url}/search/?q={product}+опт+Краснодар"
        
        try:
            response = self.session.get(search_url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем объявления (селекторы могут потребовать настройки)
            listings = soup.select('.listing-item, .product-card, .offer, .item')
            
            for item in listings[:10]:  # Берём первые 10 объявлений
                try:
                    # Пытаемся найти цену (селекторы нужно адаптировать)
                    price_elem = item.select_one('.price, .cost, .price-value')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price = self._parse_price(price_text)
                        
                        if price and price > 0:
                            results.append({
                                'product': product,
                                'price': price,
                                'currency': 'RUB',
                                'unit': 'kg',
                                'source': 'agroserver',
                                'region': TARGET_REGION
                            })
                except Exception as e:
                    continue
            
            logger.info(f"✅ Найдено {len(results)} предложений для '{product}'")
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга '{product}': {e}")
        
        # Задержка между запросами (чтобы не блокировали)
        time.sleep(random.uniform(1, 3))
        
        return results
    
    def _parse_price(self, price_text: str) -> float:
        """Очистка и парсинг цены"""
        try:
            # Удаляем всё кроме цифр, точки и запятой
            clean = ''.join(c for c in price_text if c.isdigit() or c in '.,')
            # Заменяем запятую на точку
            clean = clean.replace(',', '.')
            return float(clean)
        except:
            return 0.0
    
    def parse_all(self) -> list:
        """Парсинг всех товаров из списка"""
        all_records = []
        
        logger.info(f"🚀 Запуск парсинга {len(TARGET_PRODUCTS)} товаров...")
        
        for product in TARGET_PRODUCTS:
            records = self._search_products(product)
            all_records.extend(records)
        
        logger.info(f"📦 Всего собрано записей: {len(all_records)}")
        return all_records


# ─────────────────────────────────────────────────────────────
# Тестовый запуск
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = AgroserverParser()
    data = parser.parse_all()
    
    print(f"\n📊 Результаты парсинга:")
    for record in data[:5]:  # Показываем первые 5
        print(f"  {record['product']}: {record['price']} ₽/кг")