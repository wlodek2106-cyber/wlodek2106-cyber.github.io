import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from web3 import Web3

# Безопасно загружаем токен и настройки из переменных окружения Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RPC_URL = os.getenv("RPC_URL", "https://rpc.mainnet.chain.robinhood.com")
ZRL_TOKEN_ADDRESS = os.getenv("ZRL_TOKEN_ADDRESS", "0xВашКонтрактТокенаZRL")
PROJECT_WALLET = os.getenv("PROJECT_WALLET", "0xВашКошелекКудаПриходятZRL")

# Инициализация Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Минимальный ABI для проверки баланса ERC-20
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

# /start команда с кнопкой Web App (указан чистый корень GitHub Pages)
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
        "Нажмите кнопку ниже, чтобы открыть полноценный торговый терминал и выбрать тариф:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот Zer0life Robinhood Sniper запущен...")
    
    # Принудительно сбрасываем старые соединения, чтобы избежать конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
