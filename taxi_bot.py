import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

BOT_TOKEN = "8455450354:AAE58MVzTmEBhPk39pETWNN7zDkmcEtTD4A"
ADMIN_CHAT_ID = 1926442757

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderState(StatesGroup):
    waiting_from = State()
    waiting_to = State()

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await OrderState.waiting_from.set()
    await message.answer(
        "🚖 *Toshkent Norin Taxi*\n\n"
        "📍 Qayerdan ketasiz? (manzilni yozing)",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['bekor'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Bekor qilindi. /start - qayta boshlash")

@dp.message_handler(state=OrderState.waiting_from)
async def process_from(message: types.Message, state: FSMContext):
    await state.update_data(from_location=message.text)
    await OrderState.waiting_to.set()
    await message.answer("🏁 Qayerga borasiz? (manzilni yozing)")

@dp.message_handler(state=OrderState.waiting_to)
async def process_to(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user

    await message.answer(
        "✅ *Buyurtmangiz qabul qilindi!*\n\nHaydovchi tez orada bog'lanadi. 🚖",
        parse_mode="Markdown"
    )

    admin_msg = (
        f"🚖 *TOSHKENT NORIN TAXI — YANGI BUYURTMA*\n"
        f"{'─' * 28}\n"
        f"📍 Qayerdan: {data['from_location']}\n"
        f"🏁 Qayerga: {message.text}\n"
        f"{'─' * 28}\n"
        f"👤 Ism: {user.full_name}\n"
        f"🆔 @{user.username or 'username yoq'}\n"
        f"📱 ID: {user.id}"
    )

    await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
    await state.finish()
    
    await message.answer("Yangi buyurtma uchun /start bosing.")

@dp.message_handler()
async def unknown(message: types.Message):
    await message.answer("/start - buyurtma berish")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
