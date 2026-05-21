import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8455450354:AAE58MVzTmEBhPk39pETWNN7zDkmcEtTD4A"
ADMIN_CHAT_ID = -5107546273
GROUP_LINK = "https://t.me/toshken_norintaksi_22"
ADMIN_USERNAME = "mamasodikovs"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🚖 Taksi buyurtma"), KeyboardButton("👥 Taksi guruhlari"))
    kb.row(KeyboardButton("📞 Aloqa"))
    return kb

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🚖 Guruhimizga a'zo bo'ling", url=GROUP_LINK))
    await message.answer(
        "🚖 *Toshkent Norin Taxi*\n\n"
        "Assalomu alaykum! Xizmatimizga xush kelibsiz!\n\n"
        "🚕 Ishonchli va tez taksi xizmati\n"
        "📍 Toshkent va Norin yo'nalishi\n"
        "⏰ 24/7 xizmat\n"
        "📞 Aloqa: @mamasodikovs\n\n"
        "👇 Guruhimizga a'zo bo'ling:",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await message.answer(
        "Buyurtma berish uchun tugmani bosing:",
        reply_markup=main_menu()
    )

@dp.message_handler(lambda m: m.text == "🚖 Taksi buyurtma")
async def order_taxi(message: types.Message):
    user = message.from_user

    admin_msg = (
        f"🚖 *YANGI BUYURTMA*\n"
        f"{'─' * 28}\n"
        f"👤 Ism: {user.full_name}\n"
        f"🆔 @{user.username or 'username yoq'}\n"
        f"📱 ID: {user.id}"
    )
    await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")

    await message.answer(
        "🚕 *Shofyorlarimiz siz bilan tez orada bog'lanadi!*\n\n"
        "Xizmatimizga ishonch uchun rahmat! 😊",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@dp.message_handler(lambda m: m.text == "👥 Taksi guruhlari")
async def taxi_groups(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🚖 Norin Toshkent Taxi", url=GROUP_LINK))
    await message.answer(
        "👥 *Taksi guruhlari:*\n\nQuyidagi guruhga a'zo bo'ling:",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.message_handler(lambda m: m.text == "📞 Aloqa")
async def contact(message: types.Message):
    await message.answer(
        "📞 *Aloqa:*\n\n"
        "📱 Tel: +998 99 981 29 68\n"
        "💬 Telegram: @mamasodikovs",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@dp.message_handler()
async def unknown(message: types.Message):
    await message.answer(
        "Iltimos, quyidagi tugmalardan foydalaning:",
        reply_markup=main_menu()
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
