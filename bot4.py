from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram import Router
import asyncio

BOT_TOKEN = "8569227210:AAEm6i_N6_9ehtSZ0nwVkQ_c0a6aKkgpfHk"
CHANNEL_ID = -1003350701546  # Kanal ID raqamli bo'lishi kerak!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

classes = [
    "5.1", "5.2", "6.1","7.1",
    "8.1", "8.2", "9.1", "9.2",
    "9.3", "10.1","10.2","10.3",
    "11.1","11.2","11.3"
]

# Ovozlar va foydalanuvchi ovozlari
votes = {cls: 0 for cls in classes}
user_votes = {}  # user_id: cls


# --- 3 ustunli inline klaviatura ---
def get_keyboard():
    buttons = []
    row = []
    for i, cls in enumerate(classes, start=1):
        row.append(InlineKeyboardButton(text=f"{cls} ❤️{votes[cls]}", callback_data=f"vote_{cls}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔔 Obuna bo‘lish", url="https://t.me/zarbdormm")])
    buttons.append([InlineKeyboardButton(text="📊 Statistika", callback_data="stats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Obuna tekshiruv ---
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# --- /start buyrug'i ---
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "📢 Bayrog'imiz faxrimiz! Rasmlar tanlovida quyidagi sinflardan biriga ovoz bering.\n"
        "Rasmlar Zarbdor ixtisoslashtirilgan maktabi rasmiy kanali (https://t.me/zarbdormm) da e'lon qilingan.\n\n"
        "Quyidagi sinflardan biriga ovoz bering:",
        reply_markup=get_keyboard()
    )


# --- Ovoz berish ---
@router.callback_query(lambda c: c.data.startswith("vote_"))
async def vote_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    cls = callback.data.split("_")[1]

    if not await is_subscribed(user_id):
        await callback.answer("❗ Avval kanalga obuna bo‘ling!", show_alert=True)
        return

    if user_id in user_votes:
        await callback.answer("❗ Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    # Foydalanuvchi ovozi qo‘shildi
    votes[cls] += 1
    user_votes[user_id] = cls

    await callback.message.edit_reply_markup(reply_markup=get_keyboard())
    await callback.answer(f"{cls} sinfga ovoz berdingiz ❤️")


# --- Statistika ---
@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery):
    text = "📊 Ovozlar statistikasi:\n\n"
    for cls in classes:
        text += f"{cls}: {votes[cls]}\n"
    await callback.message.answer(text)


# --- Obunadan chiqqanlarni tekshirish ---
async def check_unsubscribed():
    while True:
        to_remove = []
        for user_id, cls in user_votes.items():
            if not await is_subscribed(user_id):
                votes[cls] -= 1
                to_remove.append(user_id)
        for user_id in to_remove:
            del user_votes[user_id]
        await asyncio.sleep(10)  # 10 soniyada bir tekshiradi


# --- Botni ishga tushirish ---
async def main():
    asyncio.create_task(check_unsubscribed())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
