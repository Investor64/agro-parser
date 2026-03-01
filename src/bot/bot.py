# src/bot/bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os
import requests
from loguru import logger

# Загружаем переменные окружения
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")
API_TOKEN = os.getenv("API_TOKEN")  # Токен для доступа к API

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────────────────────
# Клавиатура
# ─────────────────────────────────────────────────────────────
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [KeyboardButton(text="📊 Цены сегодня"), KeyboardButton(text="📈 Статистика")],
        [KeyboardButton(text="📦 Товары"), KeyboardButton(text="ℹ️ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ─────────────────────────────────────────────────────────────
# Обработчики команд
# ─────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start"""
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🥕 Я бот для мониторинга цен на овощи и фрукты в Краснодарском крае.\n\n"
        "Выберите действие в меню:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Команда /help"""
    await message.answer(
        "📖 **Помощь**\n\n"
        "📊 **Цены сегодня** — показать текущие цены\n"
        "📈 **Статистика** — статистика по товару\n"
        "📦 **Товары** — список доступных товаров\n"
        "ℹ️ **Помощь** — эта справка\n\n"
        "🔗 Команды:\n"
        "/start — Запустить бота\n"
        "/help — Показать справку\n"
        "/prices — Цены сегодня"
    )

@dp.message(F.text == "📊 Цены сегодня")
@dp.message(Command("prices"))
async def show_prices(message: types.Message):
    """Показать цены за сегодня"""
    await message.answer("⏳ Загружаю данные...")
    
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_BASE}/prices/?days=1", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                text = "📊 **Цены на сегодня**\n\n"
                for item in data[:10]:  # Первые 10 товаров
                    text += f"🥬 {item['product'].capitalize()}: {item['price']} ₽/кг\n"
                    text += f"   └─ Источник: {item['source']}\n\n"
                
                await message.answer(text, parse_mode="Markdown")
            else:
                await message.answer("⚠️ Нет данных за сегодня")
        else:
            await message.answer("❌ Ошибка получения данных")
    except Exception as e:
        logger.error(f"Ошибка в show_prices: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже")

@dp.message(F.text == "📈 Статистика")
async def show_stats(message: types.Message):
    """Показать статистику"""
    await message.answer(
        "📈 **Статистика по товарам**\n\n"
        "Отправьте название товара (например: картофель, лук, помидоры)",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📦 Товары")
async def show_products(message: types.Message):
    """Список товаров"""
    products = ["лук", "чеснок", "морковь", "картофель", "клубника", "помидоры", "огурцы"]
    text = "📦 **Доступные товары:**\n\n"
    for i, prod in enumerate(products, 1):
        text += f"{i}. {prod.capitalize()}\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "ℹ️ Помощь")
async def show_help(message: types.Message):
    """Помощь"""
    await cmd_help(message)

@dp.message(F.text)
async def handle_product_request(message: types.Message):
    """Обработка запроса статистики по товару"""
    product = message.text.lower()
    
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(
            f"{API_BASE}/prices/stats/{product}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            text = (
                f"📈 **{data['product'].capitalize()}**\n\n"
                f"💰 Текущая цена: {data['current_price']} ₽/кг\n"
                f"📊 Средняя: {data['avg_price']} ₽/кг\n"
                f"📉 Мин: {data['min_price']} ₽/кг\n"
                f"📈 Макс: {data['max_price']} ₽/кг\n"
                f"🔄 Изменение: {data['change_percent']:+.1f}%"
            )
            await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer(f"❌ Нет данных по товару: {product}")
    except Exception as e:
        logger.error(f"Ошибка в handle_product_request: {e}")
        await message.answer("❌ Произошла ошибка")

# ─────────────────────────────────────────────────────────────
# Запуск бота
# ─────────────────────────────────────────────────────────────
async def main():
    logger.info("🤖 Запуск Telegram-бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())