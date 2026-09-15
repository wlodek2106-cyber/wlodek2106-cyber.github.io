import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from web3 import Web3

# Ваш токен бота
TELEGRAM_BOT_TOKEN = "8769994364:AAHweih892xmvvRjaDd8azekZ6huM6l0HN4"
RPC_URL = "https://rpc.mainnet.chain.robinhood.com"  # Нода Robinhood Chain
ZRL_TOKEN_ADDRESS = "0xВашКонтрактТокенаZRL"
PROJECT_WALLET = "0xВашКошелекКудаПриходятZRL"

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

# /start команда с кнопкой Web App и меню
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    # Кнопка, открывающая веб-приложение
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url="https://your-mini-app-url.com")
    )
    
    builder.button(text="🚀 Тарифы и подписка", callback_data="pricing")
    builder.button(text="💎 Мой статус", callback_data="profile")
    builder.adjust(1)
    
    text = (
        "🎯 **Добро пожаловать в Zer0life Robinhood Sniper!**\n\n"
        "Бот для отслеживания новых мемкоинов в сети **Robinhood Chain** с капитализацией около $100k и фиксации крупных объемов.\n\n"
        "Нажмите кнопку ниже, чтобы открыть торговый интерфейс или выбрать раздел:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

# Меню тарифов
@dp.callback_query(F.data == "pricing")
async def cb_pricing(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Купить Lite (50 ZRL)", callback_data="buy_lite")
    builder.button(text="⚡️ Купить Pro (150 ZRL)", callback_data="buy_pro")
    builder.button(text="🔥 Купить Alpha (300 ZRL)", callback_data="buy_alpha")
    builder.button(text="⬅️ Назад", callback_data="back_home")
    builder.adjust(1)
    
    text = (
        "💳 **Тарифные пакеты Zer0life:**\n\n"
        "1️⃣ **Lite:** Базовые алерты мемкоинов (MC ~$100k).\n"
        "2️⃣ **Pro:** Мгновенные алерты + трекер крупных покупок (Volume Spikes).\n"
        "3️⃣ **Alpha:** Ранний доступ + инсайдерская аналитика кошельков.\n\n"
        "Оплата принимается исключительно в токенах **ZRL**."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "back_home")
async def cb_home(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🌐 Открыть Web App", 
        web_app=WebAppInfo(url="https://your-mini-app-url.com")
    )
    builder.button(text="🚀 Тарифы и подписка", callback_data="pricing")
    builder.button(text="💎 Мой статус", callback_data="profile")
    builder.adjust(1)
    
    text = (
        "🎯 **Zer0life Robinhood Sniper**\n\n"
        "Главное меню. Выберите нужный раздел:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def cb_buy(callback: types.CallbackQuery):
    tier = callback.data.split("_")[1].upper()
    prices = {"LITE": 50, "PRO": 150, "ALPHA": 300}
    price = prices.get(tier, 50)
    
    text = (
        f"📥 **Оформление подписки: {tier}**\n\n"
        f"Стоимость: **{price} ZRL**\n\n"
        f"Для оплаты отправьте ровно `{price}` токенов ZRL на кошелек проекта:\n"
        f"`{PROJECT_WALLET}`\n\n"
        f"После отправки напишите в поддержку или настройте автоматическое подтверждение хэша транзакции."
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def cb_profile(callback: types.CallbackQuery):
    await callback.message.answer("👤 Ваш профиль: Подписка не активна.")
    await callback.answer()

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот Zer0life Robinhood Sniper запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
