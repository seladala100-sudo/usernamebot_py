import asyncio
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8954940420:AAHO6L2naq3XO4rDrbteZIhqQ_cqwcHD_d8" 

# ── Огромный словарь слогов ──────────────────────────────────

SYLLABLES = [
    "ab","ac","ad","af","ag","ak","al","am","an","ap","ar","as","at","av","ax","az",
    "ba","be","bi","bo","bu","by","bra","bre","bri","bro","bru",
    "ca","ce","ci","co","cu","cra","cre","cri","cro","cru",
    "da","de","di","do","du","dra","dre","dri","dro","dru",
    "el","em","en","er","es","ev","ex",
    "fa","fe","fi","fo","fu","fra","fre","fri","fro","fru",
    "ga","ge","gi","go","gu","gra","gre","gri","gro","gru",
    "ha","he","hi","ho","hu","hy",
    "id","ig","il","im","in","ip","ir","is","it","iv","ix",
    "ja","je","ji","jo","ju",
    "ka","ke","ki","ko","ku","kra","kre","kri","kro",
    "la","le","li","lo","lu","ly",
    "ma","me","mi","mo","mu","my",
    "na","ne","ni","no","nu","ny",
    "ob","oc","od","of","og","ok","ol","om","on","op","or","os","ot","ov","ox",
    "pa","pe","pi","po","pu","pra","pre","pri","pro","pru",
    "ra","re","ri","ro","ru","ry",
    "sa","se","si","so","su","sy","sca","sce","sci","sco","scu","sha","she","shi","sho","shu","ska","ske","ski","sko","sku","sla","sle","sli","slo","slu","sna","sne","sni","sno","snu","spa","spe","spi","spo","spu","sta","ste","sti","sto","stu","stra","stre","stri","stro","stru",
    "ta","te","ti","to","tu","ty","tha","the","thi","tho","thu","tra","tre","tri","tro","tru",
    "ub","uc","ud","uf","ug","uk","ul","um","un","up","ur","us","ut","uv","ux",
    "va","ve","vi","vo","vu",
    "wa","we","wi","wo","wu","wra","wre","wri",
    "xa","xe","xi","xo","xu",
    "ya","ye","yi","yo","yu",
    "za","ze","zi","zo","zu",
]

# Концовки которые звучат как слово
ENDINGS = [
    "a","e","i","o","u","y",
    "al","el","il","ol","ul",
    "an","en","in","on","un",
    "ar","er","ir","or","ur",
    "as","es","is","os","us",
    "at","et","it","ot","ut",
    "ax","ex","ix","ox","ux",
    "ay","ey","oy","uy",
    "ed","id","od","ud",
    "em","im","om","um",
    "ep","ip","op","up",
    "ek","ik","ok","uk",
    "ev","iv","ov","uv",
    "ez","iz","oz","uz",
]

# Большой пул осмысленных слов 5-7 букв
WORD_POOL = [
    # 5 букв
    "blaze","frost","ghost","pixel","storm","viper","raven","sonic","nexus","prism",
    "ember","flare","vapor","blade","drake","eagle","flame","lunar","nerve","ozone",
    "phase","shade","tiger","umbra","venom","axiom","brisk","crisp","delta","forge",
    "haste","ivory","quark","racer","xenon","cobra","cyber","denim","envoy","ether",
    "exile","fable","glyph","grail","hazel","helix","joker","karma","knave","laser",
    "lumen","lyric","mauve","merge","metal","monk","mural","mystic","naive","onyx",
    "orbit","oxide","ozone","pagan","pearl","penal","plume","polar","prone","proxy",
    "pulse","purge","quill","quota","relay","remix","repel","rider","risky","rival",
    "rogue","rover","ruler","saint","salvo","scion","scout","serum","sigma","skate",
    "sleek","slick","slope","smoke","snare","sneak","solar","solid","solve","sooth",
    "spare","spark","spear","speck","spell","spend","spire","spite","splay","spore",
    "spray","squad","squat","squid","stack","staff","stage","stain","stake","stale",
    "stalk","stand","stark","start","stash","stays","steal","steam","steep","steer",
    "stern","stick","still","sting","stock","stoic","stone","stood","store","stark",
    "stray","strip","strut","stuck","study","style","suave","sulky","super","surge",
    "swamp","swear","sweep","sweet","swift","swipe","swirl","sword","synth","taboo",
    "talon","tawny","tense","tepid","texel","thane","thief","thorn","those","throb",
    "thrum","tiara","tidel","tidal","timid","titan","tonal","tonic","topaz","torso",
    "touch","toxin","trace","track","trade","trail","train","trait","tramp","trawl",
    "triad","tribe","trice","trick","tried","tripe","trite","troll","troop","troth",
    "trout","trove","truce","truck","truly","trump","trunk","tryst","tuner","tunic",
    "tweak","tweed","twice","twill","twirl","twist","tying","udder","ultra","uncut",
    "under","unify","union","unite","unity","unzip","upper","upset","usher","uvula",
    "vaunt","venal","verge","vigor","viral","visor","vista","vixen","vocal","voila",
    "vouch","vying","waken","watch","weary","wedge","weird","whack","whale","whiff",
    "while","whirl","whisk","white","whole","whose","wield","windy","wispy","witty",
    "wonky","world","worry","worse","worst","worth","wrack","wrath","wreak","wreck",
    "wrest","wring","wrist","wrote","wryly","yearn","yield","young","yours","youth",
    "zingy","zippy","zonal","zooms",
    # 6 букв
    "shadow","hunter","mystic","falcon","cipher","vector","signal","nebula","portal",
    "vortex","bishop","carbon","dagger","enigma","frenzy","herald","impact","jaguar",
    "knight","lambda","mirror","photon","quasar","ranger","sphinx","tundra","ultima",
    "warper","astral","binary","cobalt","dynamo","fusion","galaxy","ignite","kronos",
    "marble","neural","plasma","radial","reflex","riddle","rifted","robust","roping",
    "brutal","covert","cypher","darken","defcon","devoid","direkt","divine","docile",
    "domain","drifts","driven","eluded","engine","enmity","entail","envied","errant",
    "escape","evolve","exiled","exotic","expand","expose","extend","facade","factor",
    "fading","fallen","fanned","fasted","fathom","faulted","fawned","feline","fennel",
    "ferret","fervid","fester","fettle","feudal","fickle","fierce","filter","finite",
    "fisted","fitful","fitout","fixed","fizgig","flaked","flamed","flared","flaunt",
    "flexed","flight","floaty","florid","floury","fluent","flurry","flying","folder",
    "forbid","forged","formal","forted","fossil","foxtrot","fracas","framed","freely",
    "frosty","frozen","frugal","future","garnet","gibbon","gilded","glacid","glitch",
    "global","glossy","gloomy","glowed","goblin","golden","goruck","gothic","gravel",
    "grovel","growth","grunge","grassy","gravel","hasten","hinder","hidden","hybrid",
    "hydral","hyphen","icebox","impact","indent","inflow","inkjet","inline","insane",
    "intact","intuit","invent","invert","invoke","ironic","island","jester","jetset",
    "jitter","jovial","kernel","kitten","lackey","lancer","lapsed","latent","launch",
    "lavish","lawful","lawless","leader","leaned","lethal","linear","locket","lodged",
    "lunacy","luster","magnet","maiden","mangle","mantle","marrow","marvel","master",
    "matron","medium","mentor","method","metric","midair","midway","mirage","mobile",
    "modern","molten","mortal","motion","motive","mortem","mutter","nimble","nordic",
    "normal","notify","nozzle","nymph","obtuse","offset","online","oppose","oracle",
    "origin","outrun","outset","overkill","paddle","paused","pawnee","pepper","permit",
    "phases","pillar","pinned","pirate","planar","planet","plunge","pocket","poison",
    "polite","polyps","portal","posted","potent","powder","proton","punish","puppet",
    "purely","purple","pursue","puzzle","radish","ragged","rapids","rapped","rating",
    "ravage","reckless","recoil","redraw","refund","remark","remote","render","repeal",
    "replay","rescue","resist","rested","retort","return","reveal","rewind","ridged",
    "rising","robust","rocket","rooted","rotate","rugged","ruling","sacred","saddle",
    "safely","samurai","savage","scorch","sector","select","sensor","serial","shroud",
    "silent","silver","simple","single","sinker","sketch","skewed","skimpy","sleuth",
    "sliver","smooth","socket","solemn","solver","sorted","source","soviet","sprint",
    "staked","static","statue","steady","steely","strict","stride","strike","string",
    "strive","stroke","strong","struck","subtle","summit","switch","symbol","tandem",
    "target","tether","thread","threat","thrive","ticked","timber","toggle","topple",
    "torque","touchy","toward","tracer","tricky","trifle","triple","turret","unseen",
    "vacuum","valley","vanish","vanity","vertex","viable","victim","violet","virtue",
    "vision","warden","warped","weapon","wisdom","within","wizard","wombat","zenith",
    # 7 букв
    "phantom","spectre","starboy","foxfire","iceking","darkweb","neoncat","blazing",
    "thunder","shinobi","warrior","crystal","eclipse","freedom","glacial","horizon",
    "impulse","kinetic","lantern","nuclear","orbital","paradox","quantum","reactor",
    "silence","tempest","vibrant","absolut","burning","juniper","mindset","ancient",
    "article","awkward","balance","captain","captain","cascade","chronic","circuit",
    "classic","cluster","collide","command","compact","complex","conceal","conduit",
    "contour","control","courage","covered","culture","customs","default","destiny",
    "deviant","digital","distant","divided","dormant","dynasty","element","emperor",
    "endgame","endless","enforce","enhance","entrust","epsilon","evasion","evolved",
    "exhaust","faction","failing","fantasy","fatigue","figured","fighter","finance",
    "fixated","fixture","focused","foliage","follows","formula","fractal","fragile",
    "frantic","frontal","fugitive","general","genesis","glacier","graphic","gravity",
    "gridded","grimace","grizzly","grounds","habitat","hacking","handled","harmony",
    "hashmap","haunted","heading","heretic","hideous","highway","hostile","hunting",
    "iceberg","ignored","illegal","implant","imprint","indoors","inherit","injured",
    "insider","install","invader","inverse","isolate","journal","justice","kidnap",
    "kingdom","labored","lacking","landing","lateral","layered","leading","leaving",
    "library","limited","lineage","linkage","loading","lockout","maximum","measure",
    "mission","mixture","monarch","monolith","monster","mounted","neutral","newborn",
    "nightly","notable","nowhere","obscure","offense","offsite","ongoing","opening",
    "opinion","outcome","outpost","outrage","outside","package","painted","patriot",
    "pattern","pending","perfect","phantom","pilgrim","pioneer","powered","precise",
    "premier","present","primary","private","product","protect","protest","provide",
    "pursued","rampant","ranking","rapidly","reached","reality","refined","replace",
    "reserve","resolve","revival","rifting","roaming","routing","running","scanner",
    "scorned","secured","seeking","servant","service","session","shatter","shelter",
    "shifter","skyline","slanted","society","special","specter","staging","stamped",
    "startup","stealth","strayed","subject","success","suspect","survive","tactics",
    "tallied","terrain","testing","theater","thermal","timeout","tracker","trading",
    "trained","transit","trapped","trouble","trusted","turbine","twisted","unified",
    "unknown","upgrade","upright","valiant","variant","venture","version","veteran",
    "village","violent","virtual","warzone","watcher","wayward","western","willing",
    "winding","winning","without","wounded","wrapped",
]

LOADING_FRAMES = [
    "🔍 Сканирую базу...\n`▓▓░░░░░░░░░░`",
    "⚡ Стучусь к серверам...\n`▓▓▓▓░░░░░░░░`",
    "🌐 Проверяю Fragment...\n`▓▓▓▓▓▓░░░░░░`",
    "🎲 Фильтрую результаты...\n`▓▓▓▓▓▓▓▓░░░░`",
    "✨ Почти готово...\n`▓▓▓▓▓▓▓▓▓▓░░`",
    "🧠 Подбираю лучшие...\n`▓▓▓▓▓▓▓▓▓▓▓░`",
]


def generate_username(length: int) -> str:
    strategy = random.randint(1, 5)

    if strategy == 1:
        # Случайное слово нужной длины из пула
        candidates = [w for w in WORD_POOL if len(w) == length]
        if candidates:
            return random.choice(candidates).lower()

    if strategy == 2:
        # Два слога + концовка
        for _ in range(40):
            s1 = random.choice(SYLLABLES)
            s2 = random.choice(SYLLABLES)
            combo = s1 + s2
            if len(combo) == length:
                return combo.lower()
            if len(combo) < length:
                end = random.choice(ENDINGS)
                combo2 = combo + end
                if len(combo2) == length:
                    return combo2.lower()

    if strategy == 3:
        # Один слог + концовка
        for _ in range(40):
            s = random.choice(SYLLABLES)
            e = random.choice(ENDINGS)
            combo = s + e
            if len(combo) == length:
                return combo.lower()

    if strategy == 4:
        # Три слога
        for _ in range(40):
            parts = [random.choice(SYLLABLES) for _ in range(3)]
            combo = "".join(parts)
            if len(combo) == length:
                return combo.lower()

    # Fallback: нарезаем слово из пула до нужной длины + добавляем слог
    word = random.choice(WORD_POOL)
    if len(word) >= length:
        return word[:length].lower()
    syl = random.choice(SYLLABLES)
    return (word + syl)[:length].lower()


async def check_username(session: aiohttp.ClientSession, username: str) -> str:
    """
    Проверяет через Fragment API.
    Возвращает: 'free' | 'taken' | 'sale' | 'unknown'
    """
    try:
        url = f"https://fragment.com/username/{username}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            text = await resp.text()
            tl = text.lower()

            if "taken" in tl or "username is taken" in tl:
                return "taken"
            if ("buy" in tl and "ton" in tl) or "auction" in tl or "place a bid" in tl:
                return "sale"
            if ("price" in tl or "floor" in tl) and "ton" in tl:
                return "sale"
            if "not found" in tl or resp.status == 404:
                return "free"
            if "available" in tl:
                return "free"

            return "unknown"
    except Exception:
        return "unknown"


async def generate_batch(length: int, need_free: int = 5) -> dict:
    free, sale, taken = [], [], []
    checked = set()

    async with aiohttp.ClientSession() as session:
        while len(free) < need_free and len(checked) < 80:
            batch = set()
            while len(batch) < 10:
                u = generate_username(length)
                if u not in checked and u.isalpha() and len(u) == length:
                    batch.add(u)

            checked.update(batch)
            tasks = [check_username(session, u) for u in batch]
            results = await asyncio.gather(*tasks)

            for u, status in zip(batch, results):
                if status == "free" and u not in free:
                    free.append(u)
                elif status == "sale" and u not in sale:
                    sale.append(u)
                elif status == "taken" and u not in taken:
                    taken.append(u)

    return {"free": free[:need_free], "sale": sale[:4], "taken": taken[:4]}


def format_results(data: dict, length: int) -> str:
    lines = [f"━━━━━━━━━━━━━━━━━━━━━\n🎯 *Username Hunter* • {length} букв\n━━━━━━━━━━━━━━━━━━━━━\n"]

    if data["free"]:
        lines.append("🟢 *СВОБОДНЫ — бери прямо сейчас!*")
        for u in data["free"]:
            lines.append(f"  ✦ `@{u}`")
        lines.append("")
    else:
        lines.append("🟢 *Свободных не нашлось — жми ещё раз*\n")

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

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
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
            await asyncio.sleep(1.3)
            i += 1

    await asyncio.gather(do_search(), do_animation())
    return result_holder["data"]


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
