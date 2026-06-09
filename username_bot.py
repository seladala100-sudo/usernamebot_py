import asyncio
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8954940420:AAHO6L2naq3XO4rDrbteZIhqQ_cqwcHD_d8" 

PREFIXES = [
    "dark", "neo", "void", "neon", "iron", "gray", "wolf", "fox",
    "star", "moon", "ice", "fire", "sky", "red", "blue", "black",
    "ultra", "nova", "zero", "hex", "cold", "wild", "night", "dawn",
    "echo", "storm", "byte", "cyber", "pixel", "alpha", "beta", "omega"
]

SUFFIXES = [
    "x", "z", "ix", "ex", "ox", "ax", "xo", "zz", "on", "en",
    "an", "in", "ov", "ev", "is", "us", "ek", "ok", "ak", "el",
    "er", "ar", "or", "ey", "ay", "oy"
]

WORDS_5 = [
    "blaze", "frost", "ghost", "pixel", "storm", "viper", "raven",
    "sonic", "nexus", "prism", "ember", "flare", "vapor", "blade",
    "drake", "eagle", "flame", "lunar", "nerve", "ozone", "phase",
    "shade", "tiger", "umbra", "venom", "axiom", "brisk", "crisp",
    "delta", "forge", "haste", "ivory", "quark", "racer", "xenon"
]

WORDS_6 = [
    "shadow", "hunter", "mystic", "falcon", "cipher", "vector",
    "signal", "nebula", "portal", "vortex", "bishop", "carbon",
    "dagger", "enigma", "frenzy", "herald", "impact", "jaguar",
    "knight", "lambda", "mirror", "photon", "quasar", "ranger",
    "sphinx", "tundra", "ultima", "warper", "astral", "binary",
    "cobalt", "dynamo", "fusion", "galaxy", "ignite", "kronos"
]

WORDS_7 = [
    "phantom", "spectre", "starboy", "foxfire", "iceking", "darkweb",
    "neoncat", "wolfboy", "blazing", "thunder", "shinobi", "warrior",
    "crystal", "eclipse", "freedom", "glacial", "horizon", "impulse",
    "kinetic", "lantern", "nuclear", "orbital", "paradox", "quantum",
    "reactor", "silence", "tempest", "vibrant", "absolut", "burning",
    "chrome7", "darksky", "juniper", "mindset", "zephyrs"
]

WORDS_BY_LEN = {5: WORDS_5, 6: WORDS_6, 7: WORDS_7}

LOADING_FRAMES = [
    "🔍 Сканирую базу...\n`▓▓░░░░░░░░░░`",
    "⚡ Стучусь к серверам...\n`▓▓▓▓▓░░░░░░░`",
    "🌐 Проверяю Fragment...\n`▓▓▓▓▓▓▓░░░░░`",
    "🎲 Фильтрую результаты...\n`▓▓▓▓▓▓▓▓▓░░░`",
    "✨ Почти готово...\n`▓▓▓▓▓▓▓▓▓▓▓░`",
]


def generate_username(length: int) -> str:
    strategy = random.randint(1, 4)

    if strategy == 1:
        pool = WORDS_BY_LEN.get(length, WORDS_5)
        return random.choice(pool)[:length].lower()

    elif strategy == 2:
        for _ in range(30):
            p = random.choice(PREFIXES)
            s = random.choice(SUFFIXES)
            combo = (p + s)[:length]
            if len(combo) == length:
                return combo.lower()
        return random.choice(WORDS_BY_LEN.get(length, WORDS_5))[:length]

    elif strategy == 3:
        pool = WORDS_BY_LEN.get(length - 1, WORDS_5)
        word = random.choice(pool)[:length - 1]
        return (word + str(random.randint(0, 9))).lower()

    else:
        short = ["ax", "ex", "ix", "ox", "neo", "xo", "io", "vx", "nx", "rx"]
        for _ in range(30):
            a = random.choice(short)
            pool = WORDS_BY_LEN.get(length - len(a), WORDS_5)
            b = random.choice(pool)[:length - len(a)]
            combo = a + b
            if len(combo) == length:
                return combo.lower()
        return random.choice(WORDS_BY_LEN.get(length, WORDS_5))[:length]


async def check_username(session: aiohttp.ClientSession, username: str) -> str:
    """
    Проверяет юзернейм через Fragment API.
    Возвращает: 'free' | 'taken' | 'sale' | 'unknown'
    """
    try:
        # Fragment — официальный маркетплейс Telegram юзернеймов
        url = f"https://fragment.com/username/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            text = await resp.text()

            # Занят (привязан к аккаунту/каналу)
            if "taken" in text.lower() or "username is taken" in text.lower():
                return "taken"

            # Выставлен на продажу на Fragment
            if "buy" in text.lower() and "ton" in text.lower():
                return "sale"
            if "auction" in text.lower() or "place a bid" in text.lower():
                return "sale"
            if "ton" in text.lower() and ("price" in text.lower() or "floor" in text.lower()):
                return "sale"

            # Свободен — Fragment говорит что не существует
            if "not found" in text.lower() or "doesn" in text.lower():
                return "free"
            if resp.status == 404:
                return "free"

            return "unknown"

    except Exception:
        return "unknown"


async def generate_batch(length: int, need_free: int = 5) -> dict:
    """Ищет пока не найдёт need_free свободных юзернеймов"""
    free = []
    sale = []
    taken = []
    checked = set()

    async with aiohttp.ClientSession() as session:
        while len(free) < need_free and len(checked) < 60:
            # Генерируем пачку новых
            batch = set()
            while len(batch) < 8:
                u = generate_username(length)
                if u not in checked:
                    batch.add(u)

            checked.update(batch)
            tasks = [check_username(session, u) for u in batch]
            results = await asyncio.gather(*tasks)

            for u, status in zip(batch, results):
                if status == "free":
                    free.append(u)
                elif status == "sale":
                    sale.append(u)
                elif status == "taken":
                    taken.append(u)

    return {"free": free[:need_free], "sale": sale[:5], "taken": taken[:5]}


def format_results(data: dict, length: int) -> str:
    lines = [f"━━━━━━━━━━━━━━━━━━━━━\n🎯 *Username Hunter* • {length} букв\n━━━━━━━━━━━━━━━━━━━━━\n"]

    if data["free"]:
        lines.append("🟢 *СВОБОДНЫ — бери прямо сейчас!*")
        for u in data["free"]:
            lines.append(f"  ✦ `@{u}`")
        lines.append("")
    else:
        lines.append("🟢 *Свободных не найдено — попробуй ещё*\n")

    if data["sale"]:
        lines.append("🟡 *Продаются на Fragment*")
        for u in data["sale"]:
            lines.append(f"  💰 `@{u}` — [купить](https://fragment.com/username/{u})")
        lines.append("")

    if data["taken"]:
        lines.append("🔴 *Заняты*")
        for u in data["taken"]:
            lines.append(f"  · `@{u}`")
        lines.append("")

    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 Свободных: *{len(data['free'])}* | На продаже: *{len(data['sale'])}* | Занято: *{len(data['taken'])}*")

    return "\n".join(lines)


def get_keyboard(length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5️⃣", callback_data="gen_5"),
            InlineKeyboardButton("6️⃣", callback_data="gen_6"),
            InlineKeyboardButton("7️⃣", callback_data="gen_7"),
        ],
        [InlineKeyboardButton("🔄 Искать ещё", callback_data=f"gen_{length}")],
    ])


async def animate_and_search(message, length: int) -> dict:
    """Параллельно крутит анимацию и ищет"""
    result_holder = {}

    async def do_search():
        result_holder["data"] = await generate_batch(length)

    async def do_animation():
        i = 0
        while "data" not in result_holder:
            frame = LOADING_FRAMES[i % len(LOADING_FRAMES)]
            try:
                await message.edit_text(frame, parse_mode="Markdown")
            except Exception:
                pass
            await asyncio.sleep(1.2)
            i += 1

    await asyncio.gather(do_search(), do_animation())
    return result_holder["data"]


# ── ХЭНДЛЕРЫ ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 *Username Hunter*\n\n"
        "Ищу реально свободные юзернеймы через Fragment.\n"
        "Выбери длину — и начнём охоту! 🎯",
        parse_mode="Markdown",
        reply_markup=get_keyboard(5)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    length = int(query.data.split("_")[1])

    msg = await query.edit_message_text("🔍 Запускаю поиск...", parse_mode="Markdown")
    data = await animate_and_search(msg, length)

    await msg.edit_text(
        format_results(data, length),
        parse_mode="Markdown",
        reply_markup=get_keyboard(length),
        disable_web_page_preview=True
    )


async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 5
    if context.args and context.args[0].isdigit():
        length = max(4, min(8, int(context.args[0])))

    msg = await update.message.reply_text("🔍 Запускаю поиск...", parse_mode="Markdown")
    data = await animate_and_search(msg, length)

    await msg.edit_text(
        format_results(data, length),
        parse_mode="Markdown",
        reply_markup=get_keyboard(length),
        disable_web_page_preview=True
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^gen_\d$"))
    print("🤖 Username Hunter запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
