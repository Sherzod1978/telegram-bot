from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import Router
import asyncio
import matplotlib.pyplot as plt

BOT_TOKEN = "8565168044:AAERJUCshr8TtMVWiI8M4dY4X4EIjdmIvMw"
CHANNEL_ID = "-1001862491996" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Sinflar ro‘yxati
classes = [
    "5.1", "5.2", "6.1","7.1",
    "8.1", "8.2", "9.1", "9.2",
    "9.3", "10.1","10.2","10.3",
    "11.1","11.2","11.3"
]

# Ovozlar va ovoz bergan foydalanuvchilar
votes = {cls: 0 for cls in classes}
voted_users = set()

# --- Klaviatura ---
def get_keyboard():
    buttons = []

    for cls in classes:
        buttons.append(
            [InlineKeyboardButton(text=f"{cls} ❤️{votes[cls]}", callback_data=f"vote_{cls}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="🔔 Obuna bo‘lish", url="https://t.me/Zarbdor_IM")]
    )
    buttons.append(
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Obunani tekshirish ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "📢 Bayrog'imiz faxrimiz! Rasmlar tanlovida quyidagi sinflardan biriga ovoz bering.\n"
        "Rasmlar Zarbdor ixtisoslashtirilgan maktabi rasmiy kanali (https://t.me/Zarbdor_IM) da e'lon qilingan.\n\n"
        "Quyidagi sinflardan biriga ovoz bering:",
        reply_markup=get_keyboard()
    )

# Ovoz berish
@router.callback_query(F.data.startswith("vote_"))
async def vote_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    cls = callback.data.split("_")[1]

    if not await is_subscribed(user_id):
        await callback.answer("❗ Avval @Zarbdor_IM kanaliga obuna bo‘ling!", show_alert=True)
        return

    if user_id in voted_users:
        await callback.answer("❗ Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    votes[cls] += 1
    voted_users.add(user_id)

    await callback.message.edit_reply_markup(reply_markup=get_keyboard())
    await callback.answer(f"{cls} sinfga ovoz berdingiz ❤️")

# Statistika
@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery):
    # Matnli statistikani tayyorlash
    text = "📊 *Ovozlar statistikasi:*\n\n"
    for cls in classes:
        text += f"{cls}: {votes[cls]}\n"

    # Eng ko‘p ovoz olgan sinfni aniqlash
    max_votes = max(votes.values())
    winners = [cls for cls, v in votes.items() if v == max_votes and v > 0]
    if winners:
        text += f"\n🏆 Eng ko‘p ovoz olgan: {', '.join(winners)}"

    # Rasmli grafik yaratish
    plt.figure(figsize=(10,6))
    plt.bar(votes.keys(), votes.values(), color='skyblue')
    plt.xlabel('Sinflar')
    plt.ylabel('Ovozlar soni')
    plt.title('Sinflar bo‘yicha ovozlar')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("votes.png")
    plt.close()

    # Rasmni yuborish
    await callback.message.answer(text)
    await callback.message.answer_photo(photo=FSInputFile("votes.png"))

# RUN
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
