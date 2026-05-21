import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = "8455450354:AAFGVTmAJR2rc4z6a9d6UOjt5Qo4Zi62mn8"
ADMIN_CHAT_ID = 1926442757

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_from = State()
    waiting_to = State()
    waiting_confirm = State()

def confirm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("✅ Tasdiqlash"))
    kb.add(KeyboardButton("❌ Bekor qilish"))
    return kb

def phone_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Raqamni yuborish", request_contact=True))
    kb.add(KeyboardButton("❌ Bekor qilish"))
    return kb

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "🚖 *Toshkent Norin Taxi botiga xush kelibsiz!*\n\n"
        "Buyurtma berish uchun /buyurtma ni bosing.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message_handler(commands=['buyurtma'], state='*')
async def cmd_order(message: types.Message, state: FSMContext):
    await OrderState.waiting_name.set()
    await message.answer("👤 Ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=['bekor'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Bekor qilindi. /buyurtma - qayta boshlash", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(lambda m: m.text == "❌ Bekor qilish", state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Bekor qilindi. /buyurtma - qayta boshlash", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=OrderState.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await OrderState.waiting_phone.set()
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())

@dp.message_handler(content_types=types.ContentType.CONTACT, state=OrderState.waiting_phone)
async def process_phone_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await OrderState.waiting_from.set()
    await message.answer("📍 *Qayerdan* ketasiz?", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=OrderState.waiting_phone)
async def process_phone_text(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await OrderState.waiting_from.set()
    await message.answer("📍 *Qayerdan* ketasiz?", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=OrderState.waiting_from)
async def process_from(message: types.Message, state: FSMContext):
    await state.update_data(from_location=message.text)
    await OrderState.waiting_to.set()
    await message.answer("🏁 *Qayerga* borasiz?", parse_mode="Markdown")

@dp.message_handler(state=OrderState.waiting_to)
async def process_to(message: types.Message, state: FSMContext):
    await state.update_data(to_location=message.text)
    data = await state.get_data()
    summary = (
        f"📋 *Buyurtma:*\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"📍 Qayerdan: {data['from_location']}\n"
        f"🏁 Qayerga: {message.text}\n\n"
        f"Ma'lumotlar to'g'rimi?"
    )
    await OrderState.waiting_confirm.set()
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message_handler(state=OrderState.waiting_confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        user = message.from_user
        await message.answer(
            "✅ *Buyurtmangiz qabul qilindi!*\n\nHaydovchi tez orada bog'lanadi. 🚖",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        admin_msg = (
            f"🚖 *TOSHKENT NORIN TAXI — YANGI BUYURTMA*\n"
            f"👤 Ism: {data['name']}\n"
            f"📱 Telefon: {data['phone']}\n"
            f"📍 Qayerdan: {data['from_location']}\n"
            f"🏁 Qayerga: {data['to_location']}\n"
            f"🆔 @{user.username or 'username yoq'}"
        )
        await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        await state.finish()
    else:
        await message.answer("/buyurtma - qayta boshlash", reply_markup=ReplyKeyboardRemove())
        await state.finish()

@dp.message_handler()
async def unknown(message: types.Message):
    await message.answer("/buyurtma - buyurtma berish")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
