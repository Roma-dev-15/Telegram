"""
=======================================================
  БІБЛІЙНИЙ БОТ — Підтримка, Стрік, SOS, Читання
=======================================================
ВСТАНОВЛЕННЯ:
  pip install pyTelegramBotAPI schedule

ЗАПУСК:
  python bible_bot.py

ЩО ЗМІНИТИ:
  - TOKEN  → вставте свій токен від @BotFather
  - BIBLE_PLAN → можна розширити/змінити
=======================================================
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import schedule
import time
import threading
import random
from datetime import datetime, date

# ==============================================================
# 🔑 TOKEN — отримайте у @BotFather в Telegram
# ==============================================================

TOKEN = "8739979077:AAFUaoTvXXeiXfsfvLI0uDJ-1io2V90L2EQ"

bot = telebot.TeleBot(TOKEN)

# ==============================================================
# 🗃️ БАЗА КОРИСТУВАЧІВ (тимчасова, в пам'яті)
# Для постійного зберігання — можна замінити на SQLite
# ==============================================================
# Структура: { user_id: { "streak": int, "last_date": date, "name": str, "reminders": bool } }
users = {}

def get_user(user_id, name="Друже"):
    """Повертає або створює профіль користувача."""
    if user_id not in users:
        users[user_id] = {
            "streak": 0,
            "last_date": None,
            "name": name,
            "reminders": True,
            "bible_day": 1,
        }
    return users[user_id]

def update_streak(user_id):
    """Оновлює стрік — додає день якщо ще не відзначали сьогодні."""
    user = get_user(user_id)
    today = date.today()
    if user["last_date"] == today:
        return user["streak"], False  # вже відзначили сьогодні
    user["last_date"] = today
    user["streak"] += 1
    return user["streak"], True

# ==============================================================
# 📖 БІБЛІЙНІ ВІРШІ — підбадьорення
# ==============================================================
bible_quotes = [
    "«Усе можу в Христі, що дає мені силу.» — Флп. 4:13",
    "«Більший той, хто у вас, ніж той, хто у світі.» — 1 Ів. 4:4",
    "«Не переможе тебе зло, але перемагай зло добром.» — Рим. 12:21",
    "«Утікайте від блудодіяння.» — 1 Кор. 6:18",
    "«Господь — моя фортеця і скеля моя.» — Пс. 18:3",
    "«Бережіть серце своє понад усе, бо з нього — витоки життя.» — Пр. 4:23",
    "«Де грішилось гріх, там благодать надміру рясніла.» — Рим. 5:20",
    "«Твоє Слово — світильник для ноги моєї і світло для стежки моєї.» — Пс. 119:105",
    "«Відкинь усяку нечистоту і злобу й прийми Слово, що посіяне в вас.» — Як. 1:21",
    "«Я можу все через Христа — Він зміцнює мене!» — Флп. 4:13",
    "«Він знає про те, як визволити побожних від спокуси.» — 2 Пт. 2:9",
    "«Зчини опір дияволу, і він утече від тебе.» — Як. 4:7",
    "«Ти вистоїш, бо Він вірний!» — 1 Кор. 10:13",
    "«Не відкладай: покайся і будеш вільний.» — Дії 3:19",
    "«Де Дух Господній — там свобода.» — 2 Кор. 3:17",
]

# ==============================================================
# 💪 СЛОВА СИЛИ ТА ПІДБАДЬОРЕННЯ
# ==============================================================
motivation_texts = [
    "Ти — дитина Бога. Ти не раб гріху. Встань і йди!",
    "Кожен новий день — це новий шанс від Бога. Сьогодні ти переможеш!",
    "Гріх обіцяє задоволення, але дає лише порожнечу. Христос дає справжнє повнення.",
    "Ти вже пройшов стільки днів — не здавайся зараз!",
    "Свобода реальна. Тисячі людей вийшли з цієї пастки. Ти теж вийдеш.",
    "Бог бачить твою боротьбу і пишається тим, що ти встаєш щоразу.",
    "Не соромся — кайся і йди далі. Він прощає 70×7 разів.",
    "Сила — не у відсутності спокуси, а в тому, що ти обираєш щоразу.",
    "Ти більший за цей гріх. Ти покликаний до більшого!",
    "Зупинись. Подихай. Помолись. Ти справишся — Він поруч.",
    "Чистота — це не слабкість, це велика сміливість.",
    "Кожен день без зриву — це перемога. Збирай їх, як коштовності!",
]

# ==============================================================
# 🆘 SOS — дії при спокусі (ТЕРМІНОВА ДОПОМОГА)
# ==============================================================
sos_actions = [
    (
        "🚰 ВМИЙСЯ ХОЛОДНОЮ ВОДОЮ прямо зараз.\n"
        "Встань, зайди у ванну, умий обличчя холодною водою 3 рази.\n"
        "Це миттєво розриває хибний цикл думок."
    ),
    (
        "🚶 ВИЙДИ НА ВУЛИЦЮ.\n"
        "Зараз. Одягнись і вийди — не важливо куди. 10 хвилин прогулянки.\n"
        "Зміни місце — зміниш стан."
    ),
    (
        "📞 ЗАТЕЛЕФОНУЙ КОМУСЬ.\n"
        "Рідним, другу, будь-кому. Просто поговори — навіть не про це.\n"
        "Самотність — це паливо для спокуси."
    ),
    (
        "🙇 СТАНЬ НА КОЛІНА Й ПОМОЛИСЬ ВГОЛОС.\n"
        "Скажи: 'Господи, я слабкий. Врятуй мене зараз.'\n"
        "Не тихо — ВГОЛОС. Це важливо."
    ),
    (
        "🎵 УВІМКНИ ХВАЛУ.\n"
        "Відкрий YouTube: 'Christian worship' або 'хвала Богу'\n"
        "і просто слухай/співай разом. Хвала — зброя."
    ),
    (
        "📖 ВІДКРИЙ БІБЛІЮ на Псалмі 51.\n"
        "Прочитай вголос. Це молитва Давида — такого ж грішника як ти, якого Бог любив.",
    ),
    (
        "🏃 ЗРОБИ 30 ВІДЖИМАНЬ АБО ПРИСІДАНЬ.\n"
        "Фізична дія перемикає мозок. Зроби до відмови.\n"
        "Тіло — храм Святого Духа!"
    ),
    (
        "✍️ ЗАПИШИ НА ПАПЕРІ:\n"
        "1. Де я зараз?\n"
        "2. Що я відчую після зриву?\n"
        "3. Що я відчую якщо встою?\n"
        "Свідомість повертається коли пишеш."
    ),
    (
        "🌬️ ДИХАЙ: 4-7-8\n"
        "Вдих 4 секунди → Затримка 7 секунд → Видих 8 секунд.\n"
        "Повтори 4 рази. Це активує парасимпатичну систему — заспокоює миттєво."
    ),
    (
        "🧊 ТРИМАЙ КУБИК ЛЬОДУ В РУЦІ.\n"
        "Або ополосни обличчя крижаною водою.\n"
        "Холод — природний 'скид' нервової системи."
    ),
]

sos_verses = [
    "«Бог вірний, і не допустить, щоб вас спокушали понад силу вашу.» — 1 Кор. 10:13",
    "«Утікайте від юнацьких пожадань!» — 2 Тим. 2:22",
    "«Зчини опір дияволу — і він утече від тебе.» — Як. 4:7",
    "«Де Дух Господній — там свобода.» — 2 Кор. 3:17",
    "«Я прийшов, щоб мали життя, і мали вдосталь.» — Ів. 10:10",
]

# ==============================================================
# 📅 ПЛАН ЧИТАННЯ БІБЛІЇ (90 днів — скорочений варіант)
# Можна розширити до 365 днів
# ==============================================================
BIBLE_PLAN = {
    1: "Буття 1-3 — Створення світу та падіння",
    2: "Буття 4-7 — Каїн і Авель, Ной",
    3: "Буття 8-11 — Потоп закінчується, Вавилон",
    4: "Буття 12-15 — Покликання Авраама",
    5: "Псалом 1, 23, 51 — Шлях праведника, Пастир, Каяття",
    6: "Вихід 1-4 — Мойсей і горючий кущ",
    7: "Вихід 14-15 — Перехід через море",
    8: "Вихід 20 — Десять заповідей",
    9: "Приповісті 1-4 — Мудрість і застереження",
    10: "Приповісті 5-7 — Про чистоту та блудодіяння",
    11: "Псалом 91, 103, 139 — Захист, Хвала, Присутність Бога",
    12: "Ісаія 40-41 — Бог дає силу стомленим",
    13: "Ісаія 53 — Страждаючий Слуга",
    14: "Єремія 29:11-13 — Плани Бога для тебе",
    15: "Матвія 1-4 — Народження та спокуса Ісуса",
    16: "Матвія 5-7 — Нагірна проповідь",
    17: "Матвія 26-28 — Розп'яття та воскресіння",
    18: "Івана 1-3 — Бог є Любов, Нове народження",
    19: "Івана 14-17 — Утішитель, Лоза і гілки",
    20: "Римлян 1-3 — Усі згрішили",
    21: "Римлян 6-8 — Свобода від гріху",
    22: "Римлян 12 — Живи для Бога",
    23: "1 Коринтян 6 — Тіло — храм Духа Святого",
    24: "1 Коринтян 13 — Гімн любові",
    25: "Галатів 5 — Плід Духа",
    26: "Ефесян 6 — Лати Божі",
    27: "Филип'ян 4 — Мир і сила у Христі",
    28: "Якова 1-2 — Спокуса і діла",
    29: "1 Петра 1-2 — Свята поведінка",
    30: "Об'явлення 21-22 — Нове творіння і перемога",
}

def get_bible_reading(day: int) -> str:
    max_day = max(BIBLE_PLAN.keys())
    cycle_day = ((day - 1) % max_day) + 1
    return BIBLE_PLAN.get(cycle_day, "Псалом 23 — Господь Пастир мій")

# ==============================================================
# ⌨️ КЛАВІАТУРИ
# ==============================================================
def main_keyboard():
    """Головне меню — inline кнопки."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🆘 SOS — Рятуй!", callback_data="sos"),
        InlineKeyboardButton("💪 Сила слова", callback_data="motivation"),
    )
    kb.add(
        InlineKeyboardButton("📖 Вірш із Біблії", callback_data="bible_quote"),
        InlineKeyboardButton("📅 Читання Біблії", callback_data="bible_plan"),
    )
    kb.add(
        InlineKeyboardButton("🔥 Мій стрік", callback_data="streak"),
        InlineKeyboardButton("✅ Відзначити день!", callback_data="mark_day"),
    )
    kb.add(
        InlineKeyboardButton("🔄 Скинути стрік", callback_data="reset_streak"),
        InlineKeyboardButton("⚙️ Налаштування", callback_data="settings"),
    )
    return kb

def sos_keyboard():
    """Клавіатура після SOS."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🆘 Ще одна дія!", callback_data="sos"),
        InlineKeyboardButton("📖 Вірш сили", callback_data="sos_verse"),
    )
    kb.add(
        InlineKeyboardButton("💪 Слово підтримки", callback_data="motivation"),
        InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu"),
    )
    return kb

def back_keyboard():
    """Проста кнопка назад."""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu"))
    return kb

def reset_confirm_keyboard():
    """Підтвердження скидання стріку."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("😔 Так, був зрив", callback_data="confirm_reset"),
        InlineKeyboardButton("❌ Скасувати", callback_data="main_menu"),
    )
    return kb

# ==============================================================
# 📨 КОМАНДИ БОТА
# ==============================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Друже"
    get_user(user_id, name)

    welcome = (
        f"✝️ Привіт, *{name}*!\n\n"
        "Я твій помічник у боротьбі за чисте серце і духовне зростання.\n\n"
        "🔥 *Що я вмію:*\n"
        "• SOS — термінова допомога при спокусі\n"
        "• Вірші та слова підтримки\n"
        "• Відстеження стріку (дні без зриву)\n"
        "• План читання Біблії\n"
        "• Щоденні нагадування\n\n"
        "Почнемо? Обери що тобі потрібно прямо зараз 👇"
    )
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=main_keyboard())


@bot.message_handler(commands=["menu"])
def cmd_menu(message):
    bot.send_message(message.chat.id, "📋 Головне меню:", reply_markup=main_keyboard())


@bot.message_handler(commands=["sos"])
def cmd_sos(message):
    send_sos(message.chat.id, message.from_user.id)


@bot.message_handler(commands=["streak"])
def cmd_streak(message):
    user = get_user(message.from_user.id)
    streak = user["streak"]
    send_streak_info(message.chat.id, streak)


@bot.message_handler(commands=["reset_streak"])
def cmd_reset(message):
    bot.send_message(
        message.chat.id,
        "😔 Впав? Нічого — це не кінець, це новий початок.\n\nПідтвердити скидання стріку?",
        reply_markup=reset_confirm_keyboard()
    )


@bot.message_handler(commands=["verse"])
def cmd_verse(message):
    quote = random.choice(bible_quotes)
    bot.send_message(message.chat.id, f"📖 *Слово Боже:*\n\n_{quote}_", parse_mode="Markdown", reply_markup=back_keyboard())


# ==============================================================
# 🖱️ ОБРОБКА КНОПОК (callbacks)
# ==============================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    bot.answer_callback_query(call.id)  # прибирає "годинник" на кнопці

    if data == "main_menu":
        bot.send_message(chat_id, "📋 Головне меню:", reply_markup=main_keyboard())

    elif data == "sos":
        send_sos(chat_id, user_id)

    elif data == "sos_verse":
        verse = random.choice(sos_verses)
        bot.send_message(
            chat_id,
            f"⚔️ *Слово-зброя:*\n\n_{verse}_\n\n"
            "Скажи це вголос. Повтори тричі. Ти не сам!",
            parse_mode="Markdown",
            reply_markup=sos_keyboard()
        )

    elif data == "motivation":
        text = random.choice(motivation_texts)
        quote = random.choice(bible_quotes)
        bot.send_message(
            chat_id,
            f"💪 *Слово сили:*\n\n{text}\n\n"
            f"📖 _{quote}_",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )

    elif data == "bible_quote":
        quote = random.choice(bible_quotes)
        bot.send_message(
            chat_id,
            f"📖 *Слово Боже на зараз:*\n\n_{quote}_\n\n"
            "Прочитай ще раз повільно. Дай Богу говорити до тебе.",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )

    elif data == "bible_plan":
        user = get_user(user_id)
        day = user.get("bible_day", 1)
        reading = get_bible_reading(day)
        bot.send_message(
            chat_id,
            f"📅 *День {day} — план читання:*\n\n📖 {reading}\n\n"
            "Прочитай сьогодні цей уривок. Помолись перед читанням: "
            "'Господи, відкрий очі моє серце.'",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("✅ Прочитав! Далі →", callback_data="next_bible_day"),
                InlineKeyboardButton("🏠 Меню", callback_data="main_menu")
            )
        )

    elif data == "next_bible_day":
        user = get_user(user_id)
        user["bible_day"] = user.get("bible_day", 1) + 1
        day = user["bible_day"]
        reading = get_bible_reading(day)
        bot.send_message(
            chat_id,
            f"🎉 Чудово! Завтра читаєш:\n\n📅 *День {day}:* {reading}\n\n"
            "Щоденне читання Біблії — це найкращий захист!",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )

    elif data == "streak":
        user = get_user(user_id)
        send_streak_info(chat_id, user["streak"])

    elif data == "mark_day":
        streak, is_new = update_streak(user_id)
        if is_new:
            if streak == 1:
                msg = "✅ *День 1 відзначено!*\n\nПерший крок — найважливіший. Ти почав! 🎉"
            elif streak % 7 == 0:
                msg = (f"🏆 *{streak} днів без зриву!*\n\n"
                       f"Цілий тиждень — це ПЕРЕМОГА!\n"
                       f"_{random.choice(motivation_texts)}_")
            elif streak % 30 == 0:
                msg = (f"👑 *{streak} ДНІВ!*\n\n"
                       f"Цілий місяць чистоти — Бог пишається тобою!\n"
                       f"_{random.choice(bible_quotes)}_")
            else:
                msg = (f"🔥 *День {streak} відзначено!*\n\n"
                       f"_{random.choice(motivation_texts)}_")
        else:
            msg = f"👍 Ти вже відзначив сьогоднішній день!\nПоточний стрік: *{streak} днів* 🔥"

        bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "reset_streak":
        bot.send_message(
            chat_id,
            "😔 Впав? Нічого — це не кінець, це новий початок.\n\nПідтвердити скидання стріку?",
            reply_markup=reset_confirm_keyboard()
        )

    elif data == "confirm_reset":
        user = get_user(user_id)
        old_streak = user["streak"]
        user["streak"] = 0
        user["last_date"] = None
        msg = (
            f"🔄 Стрік скинуто. Попередній рекорд: *{old_streak} днів*.\n\n"
            "Не засуджуй себе — Бог вже пробачив.\n"
            "Встань, покайся, і йди далі. Починаємо з 0!\n\n"
            f"📖 _{random.choice(sos_verses)}_"
        )
        bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=main_keyboard())

    elif data == "settings":
        user = get_user(user_id)
        reminder_status = "✅ Увімкнені" if user.get("reminders", True) else "❌ Вимкнені"
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(f"🔔 Нагадування: {reminder_status}", callback_data="toggle_reminders"),
            InlineKeyboardButton("🏠 Назад", callback_data="main_menu")
        )
        bot.send_message(
            chat_id,
            "⚙️ *Налаштування*\n\nЩоденні нагадування приходять о 7:30 ранку.",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "toggle_reminders":
        user = get_user(user_id)
        user["reminders"] = not user.get("reminders", True)
        status = "✅ Увімкнені" if user["reminders"] else "❌ Вимкнені"
        bot.send_message(
            chat_id,
            f"🔔 Нагадування: *{status}*",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )


# ==============================================================
# 🆘 ФУНКЦІЯ SOS
# ==============================================================
def send_sos(chat_id, user_id):
    action = random.choice(sos_actions)
    verse = random.choice(sos_verses)

    msg = (
        "🆘 *СТІЙ! ЗУПИНИСЬ ПРЯМО ЗАРАЗ!*\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"*ЩО ЗРОБИТИ:*\n\n{action}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ *Слово Боже:*\n_{verse}_\n\n"
        "Ти НЕ ОДИН. Бог з тобою прямо зараз. 💙"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=sos_keyboard())


# ==============================================================
# 🔥 ФУНКЦІЯ СТРІКУ
# ==============================================================
def send_streak_info(chat_id, streak):
    if streak == 0:
        emoji = "🌱"
        comment = "Початок шляху. Кожна подорож починається з першого кроку!"
    elif streak < 7:
        emoji = "🔥"
        comment = "Гарний початок! Продовжуй — перший тиждень найважчий."
    elif streak < 30:
        emoji = "💪"
        comment = "Ти будуєш новий характер! Це вже справжня перемога."
    elif streak < 90:
        emoji = "🏆"
        comment = "Місяць і більше — ти справжній воїн Христа!"
    else:
        emoji = "👑"
        comment = "Неймовірно! Ти живеш у свободі. Слава Богу!"

    msg = (
        f"{emoji} *Твій стрік: {streak} днів!*\n\n"
        f"_{comment}_\n\n"
        f"📖 _{random.choice(bible_quotes)}_"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ==============================================================
# ⏰ ЩОДЕННІ НАГАДУВАННЯ (о 7:30 ранку)
# ==============================================================
def send_daily_reminder():
    """Надсилає ранкове нагадування всім користувачам з увімкненими нотифікаціями."""
    today_verse = random.choice(bible_quotes)
    today_motivation = random.choice(motivation_texts)

    for user_id, user_data in users.items():
        if user_data.get("reminders", True):
            try:
                streak = user_data.get("streak", 0)
                msg = (
                    f"☀️ *Доброго ранку, {user_data.get('name', 'Друже')}!*\n\n"
                    f"🔥 Стрік: *{streak} днів*\n\n"
                    f"📖 _{today_verse}_\n\n"
                    f"💪 {today_motivation}\n\n"
                    "Не забудь відзначити день і прочитати Біблію! 👇"
                )
                bot.send_message(user_id, msg, parse_mode="Markdown", reply_markup=main_keyboard())
            except Exception as e:
                print(f"Не вдалось надіслати нагадування {user_id}: {e}")


def run_scheduler():
    """Запускає планувальник нагадувань у окремому потоці."""
    schedule.every().day.at("07:30").do(send_daily_reminder)
    while True:
        schedule.run_pending()
        time.sleep(60)


# ==============================================================
# 🤖 ЗАПУСК БОТА
# ==============================================================
if __name__ == "__main__":
    print("✝️  Біблійний бот запущено!")
    print("📅 Нагадування о 07:30 щодня")
    print("⌨️  Натисни Ctrl+C щоб зупинити\n")

    # Запускаємо планувальник у фоні
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Запускаємо бота
    bot.polling(none_stop=True, interval=1)
