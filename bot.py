import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # Render требует порт для Web Service

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Простой HTML-код вашего мини-приложения прямо в коде бота
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zer0life Robinhood Sniper</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: Arial, sans-serif; text-align: center; padding: 50px 20px; }
        h1 { color: #38bdf8; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .btn { background: #22c55e; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>Zer0life Robinhood Sniper</h1>
    <p>Торговый терминал сети Robinhood Chain активен.</p>
    <div class="card">
        <h3>Выберите тариф</h3>
        <p>Статус подписки: <b>Активна (ZRL Holder)</b></p>
        <button class="btn" onclick="alert('Функция в разработке!')">Подключить Sniper</button>
    </div>
</body>
</html>
"""

# Обработчик встроенного сайта для Render
async def handle_index(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Бот открывает веб-сервер самого Render, а не GitHub!
    webapp_url = os.getenv("RENDER_EXTERNAL_URL", "https://zer0life-robinhood-sniper.onrender.com")
    
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url=webapp_url)
    )
    builder.adjust(1)
    
    text = (
        "🎯 **Добро пожаловать в Zer0life Robinhood Sniper!**\n\n"
        "Бот для отслеживания новых мемкоинов в сети **Robinhood Chain**.\n\n"
        "Нажмите кнопку ниже, чтобы открыть полноценный торговый терминал:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"🌐 Встроенный веб-сервер запущен на порту {PORT}")

async def main():
    # Запускаем веб-сервер для мини-приложения и самого бота параллельно
    await web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🚀 Бот запущен в режиме polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
