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

WEBAPP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://zer0life-robinhood-sniper.onrender.com")

if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ TELEGRAM_BOT_TOKEN не задан!")
    sys.exit(1)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Zer0life Robinhood Sniper</title>
    <style>
        body { background: #0b0f19; color: #f8fafc; font-family: sans-serif; text-align: center; padding: 20px; }
        .box { max-width: 400px; margin: 40px auto; background: #131c2e; padding: 24px; border-radius: 16px; border: 1px solid #1e293b; }
        h1 { color: #38bdf8; font-size: 22px; }
        .card { background: #1e293b; padding: 16px; border-radius: 12px; margin-top: 15px; text-align: left; color: #94a3b8; }
        button { background: #22c55e; color: white; border: none; width: 100%; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎯 Zer0life Sniper</h1>
        <p>Robinhood Chain Trading Terminal</p>
        <div class="card">
            <b>Статус:</b> 🟢 Онлайн<br>
            <b>Сеть:</b> Mainnet active
        </div>
        <button onclick="alert('Терминал запущен!')">Запустить Sniper</button>
    </div>
</body>
</html>"""

async def handle_everything(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Открыть Web App", web_app=WebAppInfo(url=WEBAPP_URL))
    builder.adjust(1)
    await message.answer(
        "⚡ **Zer0life Robinhood Sniper**\n\nНажмите кнопку ниже для запуска терминала:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

async def main():
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', handle_everything)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"🌐 HTTP сервер запущен на порту {PORT}, URL: {WEBAPP_URL}")

    logging.info("🚀 Запуск Telegram Polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

