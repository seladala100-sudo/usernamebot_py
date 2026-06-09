import asyncio
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telethon import TelegramClient
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.errors import FloodWaitError

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8954940420:AAHO6L2naq3XO4rDrbteZIhqQ_cqwcHD_d8")
API_ID    = int(os.environ.get("API_ID", "26548777"))
API_HASH  = os.environ.get("API_HASH", "526093a8ee7098aecbbf0033949435e1")

# Telethon клиент (userbot для проверки)
tg_client = TelegramClient("checker", API_ID, API_HASH)

# ── Словари ──────────────────────────────────────────────────

SYLLABLES = [
    "ab","ac","ad","af","ag","ak","al","am","an","ap","ar","as","at","av","ax","az",
    "ba","be","bi","bo","bu","bra","bre","bri","bro","bru",
    "ca","ce","ci","co","cu","cra","cre","cri","cro",
    "da","de","di","do","du","dra","dre","dri","dro",
    "el","em","en","er","es","ev","ex",
    "fa","fe","fi","fo","fu","fra","fre","fri","fro",
    "ga","ge","gi","go","gu","gra","gre","gri","gro",
    "ha","he","hi","ho","hu","hy",
    "id","ig","il","im","in","ip","ir","is","it","iv","ix",
    "ja","je","ji","jo","ju",
    "ka","ke","ki","ko","ku","kra","kre","kri","kro",
    "la","le","li","lo","lu","ly",
    "ma","me","mi","mo","mu","my",
    "na","ne","ni","no","nu","ny",
    "ob","oc","od","og","ok","ol","om","on","op","or","os","ot","ov","ox",
    "pa","pe","pi","po","pu","pra","pre","pri","pro",
    "ra","re","ri","ro","ru","ry",
    "sa","se","si","so","su","sy",
    "sha","she","shi","sho","shu","ska","ski","sla","sli","slo",
    "spa","spe","spi","spo","sta","ste","sti","sto","stu",
    "ta","te","ti","to","tu","ty","tha","the","thi","tho",
    "tra","tre","tri","tro","tru",
    "ub","uc","ud","ug","uk","ul","um","un","up","ur","us","ut","uv","ux",
    "va","ve","vi","vo","vu",
    "wa","we","wi","wo","wra","wre","wri",
    "xa","xe","xi","xo","xu",
    "ya","ye","yi","yo","yu",
    "za","ze","zi","zo","zu",
]

ENDINGS = [
    "a","e","i","o","u","y",
    "al","el","il","ol","ul",
    "an","en","in","on","un",
    "ar","er","ir","or","ur",
    "as","es","is","os","us",
    "ax","ex","ix","ox","ux",
    "ay","ey","oy",
    "ed","id","od",
    "em","im","om","um",
    "ek","ik","ok","uk",
    "ev","iv","ov",
]

WORD_POOL = [
    "blaze","frost","ghost","pixel","storm","viper","raven","sonic","nexus","prism",
    "ember","flare","vapor","blade","drake","eagle","flame","lunar","nerve","ozone",
    "phase","shade","tiger","umbra","venom","axiom","brisk","crisp","delta","forge",
    "haste","ivory","quark","racer","xenon","cobra","cyber","ether","exile","fable",
    "glyph","hazel","helix","joker","karma","laser","lumen","lyric","merge","metal",
    "onyx","orbit","oxide","pearl","plume","polar","proxy","pulse","purge","quill",
    "relay","remix","rider","rival","rogue","rover","saint","scion","scout","serum",
    "sigma","sleek","slick","smoke","snare","solar","solid","spare","spark","spear",
    "spell","spire","spray","squad","stack","stage","stain","stake","stalk","stark",
    "stash","steal","steam","stern","stick","sting","stock","stoic","stone","stray",
    "strip","stuck","style","suave","surge","swamp","sweep","swift","swipe","swirl",
    "sword","synth","talon","tense","thane","thief","thorn","throb","titan","tonal",
    "topaz","torso","toxin","trace","track","trade","trail","trait","triad","tribe",
    "trick","troll","trove","truce","truck","trump","trunk","tuner","tweak","twice",
    "twirl","twist","ultra","uncut","under","union","unite","upper","usher",
    "vaunt","verge","vigor","viral","visor","vista","vixen","vocal","vouch",
    "watch","weary","wedge","weird","whale","whirl","whisk","wield","windy","witty",
    "world","wrath","wreck","wrist","yearn","yield","zingy","zippy",
    "shadow","hunter","mystic","falcon","cipher","vector","signal","nebula","portal",
    "vortex","bishop","carbon","dagger","enigma","frenzy","herald","impact","jaguar",
    "knight","lambda","mirror","photon","quasar","ranger","sphinx","tundra","ultima",
    "warper","astral","binary","cobalt","dynamo","fusion","galaxy","ignite","kronos",
    "marble","neural","plasma","radial","reflex","riddle","robust","brutal","covert",
    "cypher","darken","defcon","devoid","divine","domain","driven","engine","enmity",
    "escape","evolve","exotic","expand","expose","facade","factor","fading","fallen",
    "feline","ferret","fickle","fierce","filter","finite","flight","fluent","flurry",
    "flying","forbid","forged","formal","fossil","fracas","freely","frosty","frozen",
    "future","garnet","gilded","glitch","global","glossy","goblin","golden","gothic",
    "gravel","grovel","growth","grunge","hasten","hidden","hybrid","icebox","indent",
    "inflow","insane","intact","invent","invert","invoke","ironic","island","jester",
    "kernel","kitten","lancer","latent","launch","lavish","lethal","linear","locket",
    "lunacy","luster","magnet","maiden","mangle","mantle","marvel","master","medium",
    "mentor","method","metric","midway","mirage","mobile","molten","mortal","motion",
    "mutter","nimble","nordic","normal","nozzle","offset","oppose","oracle","origin",
    "outrun","paddle","pepper","permit","pillar","pirate","planet","plunge","pocket",
    "poison","polite","portal","potent","powder","proton","punish","puppet","purely",
    "purple","pursue","puzzle","radish","ragged","rapids","ravage","recoil","redraw",
    "remark","remote","render","replay","rescue","resist","retort","return","reveal",
    "rewind","rocket","rotate","rugged","ruling","sacred","saddle","safely","savage",
    "scorch","sector","select","sensor","serial","shroud","silent","silver","simple",
    "single","sketch","sleuth","sliver","smooth","socket","solemn","solver","sorted",
    "source","sprint","static","statue","steady","steely","strict","stride","strike",
    "strive","stroke","strong","subtle","summit","switch","symbol","tandem","target",
    "tether","thread","threat","thrive","timber","toggle","topple","torque","touchy",
    "tracer","tricky","trifle","triple","turret","unseen","vacuum","valley","vanish",
    "vanity","vertex","viable","violet","virtue","vision","warden","warped","weapon",
    "wisdom","wizard","wombat","zenith",
    "phantom","spectre","blazing","thunder","shinobi","warrior","crystal","eclipse",
    "freedom","glacial","horizon","impulse","kinetic","lantern","nuclear","orbital",
    "paradox","quantum","reactor","silence","tempest","vibrant","ancient","balance",
    "captain","cascade","chronic","circuit","classic","cluster","collide","command",
    "compact","complex","conceal","conduit","control","courage","culture","default",
    "destiny","deviant","digital","distant","divided","dormant","dynasty","element",
    "emperor","endgame","endless","enforce","enhance","epsilon","evasion","evolved",
    "faction","fantasy","fatigue","fighter","finance","fixated","focused","formula",
    "fractal","fragile","frantic","frontal","general","genesis","glacier","graphic",
    "gravity","grimace","grizzly","habitat","hacking","harmony","haunted","heading",
    "heretic","highway","hostile","hunting","iceberg","illegal","implant","imprint",
    "inherit","insider","install","invader","inverse","isolate","journal","justice",
    "kingdom","lacking","landing","lateral","layered","leading","leaving","library",
    "limited","lineage","linkage","loading","lockout","maximum","measure","mission",
    "mixture","monarch","monster","mounted","neutral","newborn","nightly","notable",
    "obscure","offense","ongoing","opening","opinion","outcome","outpost","outrage",
    "outside","package","painted","patriot","pattern","pending","perfect","pilgrim",
    "pioneer","powered","precise","premier","primary","private","product","protect",
    "protest","provide","pursued","rampant","ranking","rapidly","reality","refined",
    "replace","reserve","resolve","revival","roaming","routing","running","scanner",
    "scorned","secured","seeking","servant","service","session","shatter","shelter",
    "shifter","skyline","society","special","specter","staging","stamped","startup",
    "stealth","strayed","subject","success","suspect","survive","tactics","terrain",
    "testing","theater","thermal","tracker","trading","trained","transit","trapped",
    "trusted","turbine","twisted","unified","unknown","upgrade","upright","valiant",
    "variant","venture","version","veteran","village","violent","virtual","warzone",
    "watcher","wayward","western","willing","winding","winning","without","wounded",
]

LOADING_FRAMES = [
    "🔍 Генерирую варианты...\n▱▱▱▱▱▱▱▱▱▱",
    "⚡ Проверяю через Telegram...\n▰▰▱▱▱▱▱▱▱▱",
    "🌐 Сканирую базу имён...\n▰▰▰▰▱▱▱▱▱▱",
    "🎯 Ищу свободные...\n▰▰▰▰▰▰▱▱▱▱",
    "🧠 Фильтрую результаты...\n▰▰▰▰▰▰▰▰▱▱",
    "✨ Почти готово...\n▰▰▰▰▰▰▰▰▰▱",
]


def generate_username(length: int) -> str:
    strategy = random.randint(1, 5)

    if strategy == 1:
        candidates = [w for w in WORD_POOL if len(w) == length]
        if candidates:
            return random.choice(candidates).lower()

    if strategy == 2:
        for _ in range(40):
            s1 = random.choice(SYLLABLES)
            s2 = random.choice(SYLLABLES)
            combo = s1 + s2
            if len(combo) == length:
                return combo.lower()
            if len(combo) < length:
                end = random.choice(ENDINGS)
                if len(combo + end) == length:
                    return (combo + end).lower()

    if strategy == 3:
        for _ in range(40):
            s = random.choice(SYLLABLES)
            e = random.choice(ENDINGS)
            if len(s + e) == length:
                return (s + e).lower()

    if strategy == 4:
        for _ in range(40):
            parts = [random.choice(SYLLABLES) for _ in range(3)]
            combo = "".join(parts)
            if len(combo) == length:
                return combo.lower()

    word = random.choice(WORD_POOL)
    if len(word) >= length:
        return word[:length].lower()
    syl = random.choice(SYLLABLES)
    return (word + syl)[:length].lower()


async def check_username_telethon(username: str) -> str:
    """
    Реальная проверка через Telegram MTProto.
    free / taken / flood / error
    """
    try:
        result = await tg_client(CheckUsernameRequest(username))
        return "free" if result else "taken"
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return "flood"
    except Exception:
        return "error"


async def generate_batch(length: int, need_free: int = 5) -> dict:
    free, taken = [], []
    checked = set()

    while len(free) < need_free and len(checked) < 120:
        # Генерируем батч уникальных кандидатов
        batch = []
        while len(batch) < 15:
            u = generate_username(length)
            if u not in checked and u.isalpha() and len(u) == length:
                batch.append(u)
                checked.add(u)

        # Проверяем параллельно
        tasks = [check_username_telethon(u) for u in batch]
        results = await asyncio.gather(*tasks)

        for u, status in zip(batch, results):
            if status == "free" and u not in free:
                free.append(u)
            elif status == "taken" and u not in taken:
                taken.append(u)

        # Небольшая пауза чтоб не флудить
        await asyncio.sleep(0.3)

    return {"free": free[:need_free], "taken": taken[:5]}


def format_results(data: dict, length: int) -> str:
    lines = [
        "┌─────────────────────┐",
        f"│  🎯 Username Hunter  │",
        f"│     {length} букв • Telegram  │",
        "└─────────────────────┘\n",
    ]

    if data["free"]:
        lines.append("🟢 *СВОБОДНЫ*")
        for u in data["free"]:
            lines.append(f"  ✦ `@{u}`")
        lines.append("")
    else:
        lines.append("😔 Свободных не нашлось\nПопробуй ещё раз!\n")

    if data["taken"]:
        lines.append("🔴 *Заняты*")
        for u in data["taken"]:
            lines.append(f"  · `@{u}`")
        lines.append("")

    lines.append(f"📊 Найдено свободных: *{len(data['free'])}*")
    return "\n".join(lines)


def get_keyboard(length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5️⃣ букв", callback_data="gen_5"),
            InlineKeyboardButton("6️⃣ букв", callback_data="gen_6"),
            InlineKeyboardButton("7️⃣ букв", callback_data="gen_7"),
        ],
        [InlineKeyboardButton("🔄 Ещё варианты", callback_data=f"gen_{length}")],
    ])


async def animate_and_search(message, length: int) -> dict:
    result_holder = {}

    async def do_search():
        result_holder["data"] = await generate_batch(length)

    async def do_animation():
        i = 0
        while "data" not in result_holder:
            try:
                await message.edit_text(
                    LOADING_FRAMES[i % len(LOADING_FRAMES)],
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            await asyncio.sleep(1.2)
            i += 1

    await asyncio.gather(do_search(), do_animation())
    return result_holder["data"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 *Username Hunter*\n\n"
        "Проверяю юзернеймы напрямую через Telegram.\n"
        "Только реально свободные! 🎯\n\n"
        "Выбери длину:",
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
        reply_markup=get_keyboard(length)
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
        reply_markup=get_keyboard(length)
    )


async def post_init(application):
    """Запускаем Telethon клиент вместе с ботом"""
    await tg_client.start(bot_token=BOT_TOKEN)
    print("✅ Telethon клиент подключён")


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^gen_\d$"))
    print("🤖 Username Hunter запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
