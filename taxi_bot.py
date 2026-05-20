import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = "8455450354:AAFGVTmAJR2rc4z6a9d6UOjt5Qo4Zi62mn8"
ADMIN_CHAT_ID = 1926442757

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())class OrderState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_from = State()
    waiting_to = State()
    waiting_confirm = State()

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )

def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚖 *Toshkent Norin Taxi botiga xush kelibsiz!*\n\n"
        "Boshlash uchun /buyurtma ni bosing.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Command("buyurtma"))
async def cmd_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.waiting_name)
    await message.answer(
        "👤 Ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return
    await state.update_data(name=message.text)
@dp.message(OrderState.waiting_phone, F.contact)
async def process_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await state.set_state(OrderState.waiting_from)
    await message.answer(
        "📍 *Qayerdan* ketasiz?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_phone)
async def process_phone_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return
    await state.update_data(phone=message.text)
    await state.set_state(OrderState.waiting_from)
    await message.answer(
        "📍 *Qayerdan* ketasiz?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(OrderState.waiting_from)
async def process_from(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return
    await state.update_data(from_location=message.text)
    await state.set_state(@dp.message(OrderState.waiting_to)
async def process_to(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return
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
    await state.update_data(to_location=message.text)
    await state.set_state(OrderState.waiting_confirm)
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message(OrderState.waiting_confirm)
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
        try:
            await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Xato: {e}")
        await state.clear()
    elif message.text == "❌ Bekor qilish":
        await cancel_order(message, state)

async def cancel_order(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi. /buyurtma - qayta boshlash",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Command("bekor"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await cancel_order(message, state)

@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("/buyurtma - buyurtma berish")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

