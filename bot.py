from aiogram.types import WebAppInfo  # <--- Импортируем класс для Web App

# /start команда с кнопкой Web App
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    # Кнопка, открывающая веб-приложение (укажите ссылку на ваш сайт или фронтенд)
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
        "Нажмите кнопку ниже, чтобы открыть торговый интерфейс:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())
