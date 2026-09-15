import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN не задан!")
    sys.exit(1)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Ссылка на твой сайт на GitHub Pages
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url="https://wlodek2106-cyber.github.io/")
    )
    builder.adjust(1)
    
    text = (
        "🎯 **Zer0life Robinhood Sniper**\n\n"
        "Нажмите кнопку ниже, чтобы открыть торговый терминал:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

async def main():
    logging.info("🚀 Запуск бота в режиме Polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
