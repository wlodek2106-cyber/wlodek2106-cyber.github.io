import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Загружаем токен из переменных окружения Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN не задан в переменных окружения Render!")
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url="https://wlodek2106-cyber.github.io/")
    )
    builder.adjust(1)
    
    text = (
        "🎯 **Добро пожаловать в Zer0life Robinhood Sniper!**\n\n"
        "Бот для отслеживания новых мемкоинов в сети **Robinhood Chain**.\n\n"
        "Нажмите кнопку ниже, чтобы открыть полноценный торговый терминал:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

async def main():
    logging.info("🚀 Запуск бота Zer0life Robinhood Sniper...")
    
    # Сбрасываем вебхуки и зависшие сессии перед поллингом
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning(f"⚠️ Не удалось сбросить вебхук: {e}")
        
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен.")
