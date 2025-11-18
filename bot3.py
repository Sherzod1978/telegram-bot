from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import Router
import asyncio
import matplotlib.pyplot as plt

BOT_TOKEN = "8565168044:AAERJUCshr8TtMVWiI8M4dY4X4EIjdmIvMw"
CHANNEL_ID = -1001862491996

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
user_votes = {}   # user_id : class_name


# --- Klaviatura ---
def get_keyboard():
    buttons = []
    row = []

    for i, cls in enumerate(classes, start=1):
        row.append(InlineKeyboardButton(text=f"{cls} ❤️ {votes[cls]}", callback_data=f"vote_{cls}"))
        if i % 3 == 0:  # har 3 ta tugmadan keyin yangi qator
            buttons.append(row)
            row = []

    if row:  # qolgan tugmalar uchun
        buttons.append(row)

    # Obuna tugmasi
    buttons.append([InlineKeyboardButton(text="🔔 Kanalga obuna bo‘lish", url="https://t.me/Zarbdor_IM")])
    # Statistika tugmasi
    buttons.append([InlineKeyboardButton(text="📊 Statistika", callback_data="stats")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Obunani tekshirish ---
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# --- START ---
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "📢 Bayrog'imiz faxrimiz! O‘zingizning sinfingizga ovoz bering!\n"
        "Rasmlar Zarbdor IM rasmiy kanalida joylangan.\n\n"
        "Quyidagi sinflardan biriga ovoz bering:",
        reply_markup=get_keyboard()
    )


# --- Ovoz berish ---
@router.callback_query(F.data.startswith("vote_"))
async def vote_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    cls = callback.data.split("_")[1]

    # Obuna tekshiruvi
    if not await is_subscribed(user_id):
        await callback.answer("❗ Avval @Zarbdor_IM kanaliga obuna bo‘ling!", show_alert=True)
        return

    # Tekshirish: oldin ovoz berganmi?
    if user_id in user_votes:
        await callback.answer("❗ Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    # Ovozni yozamiz
    votes[cls] += 1
    user_votes[user_id] = cls

    # Klaviaturani yangilaymiz
    await callback.message.edit_reply_markup(reply_markup=get_keyboard())
    await callback.answer(f"{cls} sinfga ovoz berdingiz ❤️")


# --- Statistika ---
@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery):
    text = "📊 *Ovozlar statistikasi:*\n\n"

    for cls in classes:
        text += f"{cls}: {votes[cls]}\n"

    # Eng ko‘p ovoz olgan sinf
    max_votes = max(votes.values())
    winners = [cls for cls, v in votes.items() if v == max_votes and v > 0]

    if winners:
        text += f"\n🏆 Eng ko‘p ovoz olgan: {', '.join(winners)}"

    # Grafik yaratamiz
    plt.figure(figsize=(10, 6))
    plt.bar(votes.keys(), votes.values(), color='skyblue')
    plt.xlabel('Sinflar')
    plt.ylabel('Ovozlar soni')
    plt.title('Sinflar bo‘yicha ovozlar')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("votes.png")
    plt.close()

    await callback.message.answer(text)
    await callback.message.answer_photo(FSInputFile("votes.png"))


# --- OBUNADAN CHIQAN FOYDALANUVCHILARNI TEKSHIRISH ---
async def check_unsubscribed():
    while True:
        remove_list = []

        for user_id, cls in list(user_votes.items()):
            if not await is_subscribed(user_id):
                # Unsubscribed – ovozini olib tashlaymiz
                if votes[cls] > 0:
                    votes[cls] -= 1

                remove_list.append(user_id)

        for user_id in remove_list:
            del user_votes[user_id]

        await asyncio.sleep(10)   # har 10 sekundda tekshiradi


# --- RUN ---
async def main():
    asyncio.create_task(check_unsubscribed())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
