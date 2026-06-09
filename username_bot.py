import asyncio
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8954940420:AAHO6L2naq3XO4rDrbteZIhqQ_cqwcHD_d8"

# ── Смысловые части для генерации ──────────────────────────
PREFIXES = [
    "dark", "neo", "void", "neon", "iron", "gray", "wolf", "fox",
    "star", "moon", "sun", "ice", "fire", "sky", "red", "blue",
    "black", "ultra", "mega", "hyper", "nova", "zero", "hex",
    "cold", "wild", "sharp", "night", "dawn", "dusk", "echo",
    "storm", "byte", "cyber", "pixel", "alpha", "beta", "omega"
]

SUFFIXES = [
    "x", "z", "ix", "ex", "ox", "ax", "xo", "zz", "xx",
    "on", "en", "an", "in", "un", "ov", "ev", "is", "us",
    "ek", "ok", "ak", "ik", "uk", "el", "al", "ul", "il",
    "er", "ar", "or", "ir", "ur", "ey", "ay", "oy"
]

WORDS_5 = [
    "blaze", "frost", "ghost", "pixel", "storm", "viper", "raven",
    "sonic", "nexus", "prism", "gloom", "ember", "flare", "vapor",
    "blade", "crane", "drake", "eagle", "flame", "grail", "hazel",
    "indie", "joker", "krait", "lunar", "magic", "nerve", "ozone",
    "phase", "quark", "racer", "shade", "tiger", "umbra", "venom",
    "wired", "xenon", "yodel", "zebra", "axiom", "brisk", "crisp",
    "delta", "epoch", "forge", "graze", "haste", "ivory", "jelly"
]

WORDS_6 = [
    "shadow", "hunter", "mystic", "falcon", "cipher", "vector",
    "signal", "nebula", "portal", "vortex", "specter", "bishop",
    "carbon", "dagger", "enigma", "frenzy", "glacer", "herald",
    "impact", "jaguar", "knight", "lambda", "mirror", "nitros",
    "onyx", "photon", "quasar", "ranger", "sphinx", "tundra",
    "ultima", "Viking", "warper", "xypher", "yakuza", "zealot",
    "astral", "binary", "cobalt", "dynamo", "ether", "fusion",
    "galaxy", "hydra", "ignite", "jarvis", "kronos", "lucent"
]

WORDS_7 = [
    "phantom", "spectre", "vortexz", "starboy", "foxfire", "iceking",
    "darkweb", "cyberxz", "neoncat", "wolfboy", "blazing", "thunder",
    "shinobi", "warrior", "ancient", "crystal", "darksky", "eclipse",
    "freedom", "glacial", "horizon", "impulse", "juniper", "kinetic",
    "lantern", "mindset", "nuclear", "orbital", "paradox", "quantum",
    "reactor", "silence", "tempest", "unicorn", "vibrant", "weather",
    "xtreme", "yellowy", "zephyrs", "absolut", "burning", "chrome"
]

WORDS_BY_LEN = {5: WORDS_5, 6: WORDS_6, 7: WORDS_7}

# Анимация загрузки
LOADING_FRAMES = [
    "🔍 Сканирую базу...",
    "⚡ Проверяю доступность...",
    "🌐 Стучусь к серверам...",
    "🎲 Подбираю варианты...",
    "✨ Почти готово...",
]

def generate_username(length: int) -> str:
    strategy = random.randint(1, 4)

    if strategy == 1:
        # Готовое слово нужной длины
        pool = WORDS_BY_LEN.get(length, WORDS_5)
        word = random.choice(pool)
        return word[:length].lower()

    elif strategy == 2:
        # Префикс + суффикс подогнать под длину
        for _ in range(20):
            p = random.choice(PREFIXES)
            s = random.choice(SUFFIXES)
            combo = (p + s)[:length]
            if len(combo) == length:
                return combo.lower()
        return random.choice(WORDS_BY_LEN.get(length, WORDS_5))[:length]

    elif strategy == 3:
        # Слово + цифра
        pool = WORDS_BY_LEN.get(length - 1, WORDS_5)
        word = random.choice(pool)[: length - 1]
        return (word + str(random.randint(0, 9))).lower()

    else:
        # Два мини-слова склеить
        short = ["ax", "ex", "ix", "ox", "neo", "xo", "io", "yz",
                 "zx", "vx", "kx", "qx", "jx", "rx", "nx", "mx"]
        for _ in range(20):
            a = random.choice(short)
            pool = WORDS_BY_LEN.get(length - len(a), WORDS_5)
            b = random.choice(pool)[: length - len(a)]
            combo = a + b
            if len(combo) == length:
                return combo.lower()
        return random.choice(WORDS_BY_LEN.get(length, WORDS_5))[:length]


async def check_username(username: str):
    url = f"https://t.me/{username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                text = await resp.text()
                if "tgme_page_extra" in text or "tgme_page_photo" in text:
                    return False
                return True
    except Exception:
        return None


async def generate_batch(length: int, count: int = 12) -> list:
    candidates = set()
    while len(candidates) < count * 2:
        candidates.add(generate_username(length))

    picked = list(candidates)[:count]
    tasks = [check_username(u) for u in picked]
    statuses = await asyncio.gather(*tasks)
    return [{"username": u, "available": s} for u, s in zip(picked, statuses)]


def format_results(results: list, length: int) -> str:
    free = [r for r in results if r["available"] is True]
    taken = [r for r in results if r["available"] is False]
    unknown = [r for r in results if r["available"] is None]

    lines = [f"━━━━━━━━━━━━━━━━━━━━━\n🎯 Юзернеймы • {length} букв\n━━━━━━━━━━━━━━━━━━━━━\n"]

    if free:
        lines.append("🟢 *СВОБОДНЫ* — бери быстрее!")
        for r in free:
            lines.append(f"  ✦ `@{r['username']}`")
        lines.append("")

    if taken:
        lines.append("🔴 *Заняты*")
        for r in taken:
            lines.append(f"  · `@{r['username']}`")
        lines.append("")

    if unknown:
        lines.append("⚪️ *Не проверить*")
        for r in unknown:
            lines.append(f"  · `@{r['username']}`")
        lines.append("")

    free_count = len(free)
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 Найдено свободных: *{free_count}* из {len(results)}")

    return "\n".join(lines)


def get_keyboard(length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5️⃣ букв", callback_data="gen_5"),
            InlineKeyboardButton("6️⃣ букв", callback_data="gen_6"),
            InlineKeyboardButton("7️⃣ букв", callback_data="gen_7"),
        ],
        [InlineKeyboardButton("🔄 Искать ещё", callback_data=f"gen_{length}")],
    ])


async def animate_loading(message, length: int):
    """Крутит анимацию загрузки пока ищем"""
    for frame in LOADING_FRAMES:
        try:
            await message.edit_text(
                f"{frame}\n\n`{'▓' * random.randint(3,12)}{'░' * random.randint(3,8)}`",
                parse_mode="Markdown"
            )
            await asyncio.sleep(0.8)
        except Exception:
            break


async def search_with_animation(message, length: int):
    """Запускает анимацию и поиск параллельно"""
    anim_task = asyncio.create_task(animate_loading(message, length))
    results = await generate_batch(length)
    anim_task.cancel()
    return results


# ── ХЭНДЛЕРЫ ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👾 *Username Hunter*\n\n"
        "Нахожу красивые свободные юзернеймы в Telegram.\n"
        "Выбери длину — и начнём охоту! 🎯"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_keyboard(5))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    length = int(query.data.split("_")[1])

    msg = await query.edit_message_text("🔍 Начинаю поиск...", parse_mode="Markdown")
    results = await search_with_animation(msg, length)

    await msg.edit_text(
        format_results(results, length),
        parse_mode="Markdown",
        reply_markup=get_keyboard(length)
    )


async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 5
    if context.args and context.args[0].isdigit():
        length = max(4, min(8, int(context.args[0])))

    msg = await update.message.reply_text("🔍 Начинаю поиск...", parse_mode="Markdown")
    results = await search_with_animation(msg, length)

    await msg.edit_text(
        format_results(results, length),
        parse_mode="Markdown",
        reply_markup=get_keyboard(length)
    )


# ── ЗАПУСК ───────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^gen_\d$"))
    print("🤖 Username Hunter запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
