"""
Toshkent Norin Taxi - Buyurtma boti
Ishlatish uchun:
1. pip install aiogram
2. BOT_TOKEN va ADMIN_CHAT_ID ni o'zgartiring
3. python taxi_bot.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ========================
# SOZLAMALAR
# ========================
BOT_TOKEN = "8455450354:AAFGVTmAJR2rc4z6a9d6UOjt5Qo4Zi62mn8"  # Toshkent Norin Taxi
ADMIN_CHAT_ID = 1926442757               # Toshkent Norin Taxi admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ========================
# HOLATLAR (FSM)
# ========================
class OrderState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_from = State()
    waiting_to = State()
    waiting_confirm = State()


# ========================
# KLAVIATURALAR
# ========================
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
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )


# ========================
# /start
# ========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚖 *Toshkent Norin Taxi botiga xush kelibsiz!*\n\n"
        "Men sizga tez va qulay tarzda taksi buyurtma qilishda yordam beraman.\n\n"
        "Boshlash uchun /buyurtma ni bosing.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )


# ========================
# /buyurtma - Buyurtma boshlash
# ========================
@dp.message(Command("buyurtma"))
async def cmd_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.waiting_name)
    await message.answer(
        "👤 Ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )


# ========================
# ISM
# ========================
@dp.message(OrderState.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return

    await state.update_data(name=message.text)
    await state.set_state(OrderState.waiting_phone)
    await message.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard()
    )


# ========================
# TELEFON
# ========================
@dp.message(OrderState.waiting_phone, F.contact)
async def process_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await state.set_state(OrderState.waiting_from)
    await message.answer(
        "📍 *Qayerdan* ketasiz? (manzilni yozing):",
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
        "📍 *Qayerdan* ketasiz? (manzilni yozing):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )


# ========================
# QAYERDAN
# ========================
@dp.message(OrderState.waiting_from)
async def process_from(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return

    await state.update_data(from_location=message.text)
    await state.set_state(OrderState.waiting_to)
    await message.answer("🏁 *Qayerga* borasiz? (manzilni yozing):", parse_mode="Markdown")


# ========================
# QAYERGA
# ========================
@dp.message(OrderState.waiting_to)
async def process_to(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
        return

    await state.update_data(to_location=message.text)
    data = await state.get_data()

    summary = (
        f"📋 *Buyurtma ma'lumotlari:*\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"📍 Qayerdan: {data['from_location']}\n"
        f"🏁 Qayerga: {message.text}\n\n"
        f"Ma'lumotlar to'g'rimi?"
    )

    await state.set_state(OrderState.waiting_confirm)
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


# ========================
# TASDIQLASH
# ========================
@dp.message(OrderState.waiting_confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        user = message.from_user

        # Foydalanuvchiga xabar
        await message.answer(
            "✅ *Buyurtmangiz qabul qilindi!*\n\n"
            "Haydovchi tez orada siz bilan bog'lanadi. 🚖",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )

        # Adminga xabar
        admin_msg = (
            f"🚖 *TOSHKENT NORIN TAXI — YANGI BUYURTMA*\n"
            f"{'─' * 28}\n"
            f"👤 Ism: {data['name']}\n"
            f"📱 Telefon: {data['phone']}\n"
            f"📍 Qayerdan: {data['from_location']}\n"
            f"🏁 Qayerga: {data['to_location']}\n"
            f"{'─' * 28}\n"
            f"🆔 Telegram: @{user.username or 'username yo\'q'}\n"
            f"🔢 ID: {user.id}"
        )

        try:
            await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Admin ga xabar yuborishda xato: {e}")

        await state.clear()

    elif message.text == "❌ Bekor qilish":
        await cancel_order(message, state)
    else:
        await message.answer("Iltimos, tugmalardan birini bosing.")


# ========================
# BEKOR QILISH
# ========================
async def cancel_order(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Buyurtma bekor qilindi.\n\nQayta buyurtma berish uchun /buyurtma ni bosing.",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Command("bekor"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await cancel_order(message, state)


# ========================
# NOMA'LUM XABARLAR
# ========================
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "Buyurtma berish uchun /buyurtma ni bosing.\n"
        "Bekor qilish uchun /bekor ni bosing."
    )


# ========================
# ISHGA TUSHIRISH
# ========================
async def main():
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
