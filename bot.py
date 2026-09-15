import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_URL:
    WEBAPP_URL = "https://zer0life-robinhood-sniper.onrender.com"
else:
    WEBAPP_URL = RENDER_URL

if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN не задан!")
    sys.exit(1)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zer0life Robinhood Sniper</title>
    <style>
        body { background: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 20px; margin: 0; }
        .container { max-width: 400px; margin: 40px auto; background: #131c2e; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #1e293b; }
        h1 { color: #38bdf8; font-size: 22px; margin-bottom: 8px; }
        p { color: #94a3b8; font-size: 14px; }
        .card { background: #1e293b; padding: 16px; border-radius: 12px; margin-top: 20px; text-align: left; }
        .card-title { font-weight: bold; color: #f8fafc; margin-bottom: 6px; }
        .btn { background: #22c55e; color: white; border: none; width: 100%; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; margin-top: 20px; }
        .btn:active { background: #16a34a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Zer0life Sniper</h1>
        <p>Robinhood Chain Trading Terminal</p>
        <div class="card">
            <div class="card-title">Статус системы</div>
            <p>🟢 Бот активен • Сеть: Online</p>
        </div>
        <div class="card">
            <div class="card-title">Кошелек / Токен</div>
            <p>ZRL Holder • Готов к охоте</p>
        </div>
        <button class="btn" onclick="alert('Снайпер успешно активирован!')">Запустить Sniper</button>
    </div>
</body>
</html>
"""

# Функция, которая гарантированно шлет HTML на любой запрос
async def handle_all(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    builder.adjust(1)
    
    text = (
        "⚡ **Zer0life Robinhood Sniper**\n\n"
        "Торговый терминал готов к работе.\n"
        "Нажмите кнопку ниже для запуска интерфейса:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

async def start_web_server():
    app = web.Application()
    # Вешаем обработчик на абсолютно любые пути и методы
    app.router.add_route('*', '/{tail:.*}', handle_all)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"🌐 Железобетонный веб-сервер запущен на порту {PORT}")

async def main():
    await start_web_server()
    logging.info("🚀 Запуск Telegram бота в режиме polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
