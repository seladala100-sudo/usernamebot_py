import asyncio
import random
import string
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ⚙️ ВСТАВЬ СВОЙ ТОКЕН СЮДА
BOT_TOKEN = "8954940420:AAHO6L2naq3XO4rDrbteZIhqQ_cqwcHD_d8"

CONSONANTS = "bcdfghjklmnpqrstvwxyz"
VOWELS = "aeiou"

def generate_username(length: int = 5) -> str:
    patterns = [
        lambda: "".join(
            random.choice(VOWELS) if i % 2 == 0 else random.choice(CONSONANTS)
            for i in range(length)
        ),
        lambda: "".join(random.choices(string.ascii_lowercase, k=length)),
        lambda: "".join(
            random.choice(CONSONANTS) if i % 2 == 0 else random.choice(VOWELS)
            for i in range(length)
        ),
    ]
    return random.choice(patterns)()


async def check_username_available(username: str):
    url = f"https://t.me/{username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                text = await resp.text()
                if "tgme_page_extra" in text or "tgme_page_photo" in text:
                    return False
                return True
    except Exception:
        return None


async def generate_batch(count: int = 10, length: int = 5) -> list:
    candidates = set()
    while len(candidates) < count * 2:
        candidates.add(generate_username(length))

    picked = list(candidates)[:count]
    tasks = [check_username_available(u) for u in picked]
    statuses = await asyncio.gather(*tasks)

    return [{"username": f"@{u}", "available": s} for u, s in zip(picked, statuses)]


def format_results(results: list) -> str:
    lines = []
    for r in results:
        if r["available"] is True:
            lines.append(f"✅ `{r['username']}` — свободен")
        elif r["available"] is False:
            lines.append(f"❌ `{r['username']}` — занят")
        else:
            lines.append(f"❓ `{r['username']}` — не проверить")
    return "\n".join(lines)


def get_keyboard(length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5 букв", callback_data="gen_5"),
            InlineKeyboardButton("6 букв", callback_data="gen_6"),
            InlineKeyboardButton("7 букв", callback_data="gen_7"),
        ],
        [InlineKeyboardButton("🔄 Ещё раз", callback_data=f"gen_{length}")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 *Username Generator*\n\n"
        "Генерирую короткие свободные юзернеймы для Telegram.\n"
        "Выбери длину — и погнали!",
        parse_mode="Markdown",
        reply_markup=get_keyboard(5)
    )


async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 5
    if context.args and context.args[0].isdigit():
        length = max(4, min(8, int(context.args[0])))

    msg = await update.message.reply_text(f"⏳ Генерирую {length}-буквенные юзернеймы...")
    results = await generate_batch(count=10, length=length)
    await msg.edit_text(
        f"🎲 *Юзернеймы ({length} букв):*\n\n{format_results(results)}",
        parse_mode="Markdown",
        reply_markup=get_keyboard(length)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    length = int(query.data.split("_")[1])

    await query.edit_message_text(f"⏳ Генерирую {length}-буквенные юзернеймы...")
    results = await generate_batch(count=10, length=length)
    await query.edit_message_text(
        f"🎲 *Юзернеймы ({length} букв):*\n\n{format_results(results)}",
        parse_mode="Markdown",
        reply_markup=get_keyboard(length)
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^gen_\d$"))
    print("🤖 Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
