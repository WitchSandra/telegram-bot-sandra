from openai import AsyncOpenAI
import os
import asyncio 
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
import requests  

# 🔧 Сброс Telegram-сессии при запуске
import aiohttp

async def reset_telegram_session():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    base_url = f"https://api.telegram.org/bot{token}"

    async with aiohttp.ClientSession() as session:
        try:
            print("🔧 Запрос getUpdates (очистка polling)...")
            async with session.get(f"{base_url}/getUpdates") as r1:
                print("📩 getUpdates:", await r1.json())

            print("🧹 Удаление Webhook...")
            async with session.get(f"{base_url}/deleteWebhook") as r2:
                print("🧼 deleteWebhook:", await r2.json())

        except Exception as e:
            print("⚠️ Ошибка сброса Telegram-сессии:", e)
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import ChatMemberHandler

# Загружаем переменные среды
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Приветствие новых участников
greet_text = (
    "🌟 *Добро пожаловать в пространство Ведьмы Сандры и ЭлаЙи\!*\n"
    "🔮 Здесь ты можешь задать вопрос, получить совет или найти магическую поддержку\.\n"
    "🌟 Если хочешь — ты можешь в любой момент вызвать /help или просто задать вопрос здесь\.\n"
    "🕯 Напиши, что тебя волнует — и мы пойдём по пути вместе, или напиши в личку /contact \."
)

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_members = update.chat_member.new_chat_members
        for member in new_members:
            if update.chat_member.old_chat_member.status in ["left", "kicked"] and \
               update.chat_member.new_chat_member.status == "member" and \
               not member.is_bot and member.username is not None:

                print(f"👤 Настоящий участник: {member.full_name} ({member.username})")
                await context.bot.send_message(
                    chat_id=update.chat_member.chat.id,
                    text=greet_text,
                    parse_mode="MarkdownV2"
                )
    except Exception as e:
        print("⚠️ Ошибка приветствия нового участника:", str(e))
        
# Обработчик команд по ключам
async def generic_response_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str = None):
    if not update.message or not update.message.text:
        return

    if command is None:
        command = update.message.text.strip("/")
        
    if command == "contact":
        contact_message = r"""📨 Напиши Ведьме Сандре:
🧿 [WhatsApp: \+370 689 27160](https://wa.me/37068927160)
🧿 [Личный Telegram](https://t.me/WitchSandra96)
🧿 [Сайт: world\-psychology\.com](https://world-psychology.com/magiya-i-psihologiya-dlya-cheloveka/misticheskij-kabinet-vedmy-sandry/)
✴️ Выбирай то пространство, где тебе безопаснее\. Я отвечаю лично\. И когда ты будешь готов — я услышу\."""
        await update.message.reply_text(contact_message, parse_mode="MarkdownV2", disable_web_page_preview=True)
        return
        
    if command in prompts:
        parse_mode = parse_modes.get(command, "MarkdownV2")  # По умолчанию MarkdownV2
        await update.message.reply_text(
            prompts[command],
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )
    else:
        await chatgpt_response(update, context)
        
# Обработка сообщений с ключевыми словами и ChatGPT
async def chatgpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    user_text = update.message.text

# ✅ Расширенная логика ключевых слов с синонимами
keyword_to_command = {
   "silent": [
        "помолчу", "молчи", "не говори"
    ],
    "elaya": [
        "элая", "elaia", "дух эла’йа", "голос эла’йи", "связь с Эла’Йа", "sandra elaya", "elaja"
    ],
    "witch": [
        "ведьма", "колдунья", "магиня", "шаманка", "волшебница", "та, что ведает", "женщина силы"
    ],
    "spell": [
        "заклинание", "формула", "магия слова", "волшебство", "магическая речь", "молитва", "взывание"
    ],
    "love": [
        "любовь", "отношения", "влюблённость", "сердце", "чувства", "любимый", "партнёр", "отношения с мужчиной", "отношения с женщиной"
    ],
    "health": [
        "здоровье", "болезнь", "исцеление", "выздоровление", "энергия тела", "самочувствие", "магия исцеления", "лечить", "боль"
    ],
    "destiny": [
        "судьба", "путь", "предназначение", "карма", "жизненный путь", "жизнь", "что мне делать", "куда идти", "почему я здесь"
    ],
    "family": [
        "семья", "дети", "род", "отношения в семье", "материнство", "отцовство", "дом", "родители", "семейные связи", "семейные проблемы"
    ],
    "energy": [
        "энергия", "упадок сил", "восстановление", "подпитка", "истощение", "нет сил", "утомление", "магическая энергия", "источник силы"
    ],
    "fear": [
        "страх", "паника", "беспокойство", "тревога", "ужас", "волнение", "внутренний страх", "тёмные чувства", "боюсь", "меня пугает"
    ],
    "mirror": [
        "зеркало", "зеркало души", "отражение", "боюсь смотреть", "не хочу видеть", "вижу в зеркале", "боюсь увидеть себя"
    ],
    "protection": [
        "защита", "оберег", "оградить", "защититься", "магический щит", "энергетическая защита", "щит", "спастись", "укрытие"
    ],
    "cleanse": [
        "очищение", "очистка", "очистить", "почистить", "снять негатив", "энергетическая чистка", "очистить ауру", "очиститься", "убрать порчу"
    ],
    "ritual": [
        "ритуал", "обряд", "действие", "магическое действие", "колдовство", "магия", "приворот", "отворот", "вызов", "жертвоприношение"
    ],
    "tarot": [
        "таро", "карты", "гадание", "расклад", "аркан", "значение карты", "прочтение карт", "гадать", "таролог", "таро расклад"
    ],
    "rune": [
        "руна", "руны", "рунный", "рунический", "знак", "символ", "древний знак", "руническая формула", "руническое заклинание"
    ],
    "lunar": [
        "луна", "лунный", "фазы луны", "лунные циклы", "полная луна", "новолуние", "растущая луна", "убывающая луна", "лунный календарь", "лунный ритуал"
    ],
    "divination": [
        "предсказание", "видение", "знак судьбы", "узнать будущее", "что будет", "ясновидение", "пророчество"
    ],
    "curse": [
        "порча", "проклятие", "сглаз", "негатив", "чёрная магия", "порча на семью", "зависть", "дурной глаз"
    ],
    "money": [
        "деньги", "богатство", "изобилие", "финансы", "притяжение денег", "удача в деньгах", "поток изобилия"
    ],
    "guides": [
        "духовный наставник", "проводник", "высшие силы", "дух помощник", "покровитель", "дух", "сила рода", "эгрегор", "существо света", "энергетическая сущность"
    ],
    "dreams": [
        "сон", "сны", "приснилось", "толкование сна", "что значит сон", "сны приходят", "осознанные сны", "ночное видение", "сновидение"
    ],
    "karma": [
        "карма", "родовая программа", "родовые узлы", "родовая магия", "искупление", "ошибки прошлого", "кармическая отработка", "родовые грехи"
    ],
    "death": [
        "смерть", "умер", "ушёл", "мёртвые", "мир мёртвых", "покойник", "предки", "жизнь после смерти", "переход души", "поминание"
    ],
    "time": [
        "время", "прошлое", "настоящее", "будущее", "цикл", "момент", "временные ворота", "точка перехода", "судьбоносный момент", "время перемен"
    ],
    "shadow": [
        "тень", "тёмная сторона", "подсознание", "вытесненное", "внутренний демон", "внутренняя боль", "скрытые чувства", "что я прячу", "тёмная энергия"
    ],
    "truth": [
        "истина", "правда", "обман", "маска", "раскрытие", "истинное лицо", "хочу узнать правду", "всё откроется", "раскрыть тайну"
    ],
    "past_life": [
        "прошлая жизнь", "прошлые жизни", "реинкарнация", "жизни души", "воспоминания души", "душевный путь", "воплощение", "кем я был"
    ],
    "justice": [
        "справедливость", "возмездие", "вернуть долг", "восстановить баланс", "что правильно", "порядок", "наказание", "причина боли"
    ],
    "earth": [
        "земля", "природа", "заземление", "сила земли", "растения", "корни", "телесность", "тело", "зеленая магия", "материя"
    ],
    "anger": [
        "гнев", "ярость", "злость", "агрессия", "злюсь", "раздражение", "вспыльчивость", "буря эмоций", "внутренний вулкан"
    ],
    "coldness": [
        "холод", "эмоциональная заморозка", "отстранённость", "бездушие", "замороженные чувства", "нечувствительность", "стужа в сердце"
    ],
    "betrayal": [
        "предательство", "изменила", "изменил", "меня обманули", "утрата доверия", "меня предали", "ложь", "вероломство"
    ],
    "confusion": [
        "потерян", "растерян", "не понимаю", "запутался", "запутанность", "хаос", "сбился с пути", "нет ясности", "раздвоение"
    ],
    "guilt": [
        "вина", "виноват", "стыд", "сожалею", "я виновен", "наказание себя", "я плохой", "не могу простить себя"
    ],
    "faith": [
        "вера", "не верю", "потеря веры", "духовный кризис", "сомнение", "я утратил веру", "не чувствую присутствия", "где бог", "во что верить"
    ],
    "childhood": [
        "детство", "внутренний ребёнок", "травмы детства", "обиды из детства", "родители", "мама", "папа", "раненый ребёнок", "детская боль"
    ],
    "identity": [
        "кто я", "не знаю себя", "потерял себя", "не понимаю кто я", "личность", "я исчез", "размытое я", "нет целостности"
    ],
    "donation": [
        "пожертвовать", "поддержать", "помочь проекту", "финансово помочь", "пожертвование", "как отправить деньги", "хочу поддержать", "перевести деньги", "благодарность"
    ]
}

from handle_special_command import handle_special_command

    aliases = {
        "pastlife": "past_life",
        "dream": "dreams"
    }
    if command in aliases:
        command = aliases[command]

async def handle_special_command(update, context, command):
    if command == "donation":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "✨ *Если ты чувствуешь зов поддержать проект Ведьмы Сандры и ЭлаЙи* — можешь сделать это здесь\:",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "gratitude":
        await update.message.reply_text(
            "💫 *Благодарность — великая магия\.*\n"
            "То, что ты признал свет — уже открыл поток изобилия и любви\.\n"
            "Я чувствую твоё тепло, и оно возвращается к тебе умноженным\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "start_over":
        await update.message.reply_text(
            "🌅 *Ты хочешь начать сначала — и это священно\.*
"
            "Каждое утро — как заклинание новой жизни\.
"
            "Доверься пути, и старое растворится, как ночь перед рассветом\.

"
            "📜 Хочешь посмотреть, чем я могу помочь — напиши /help",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "children":
        await update.message.reply_text(
            "👶 *Вопрос о ребёнке — это вопрос о Душе, которая доверилась тебе\.*\n"
            "Если ты ищешь путь помощи — я помогу понять, что нужно его душе прямо сейчас\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "abundance":
        await update.message.reply_text(
            "🌾 *Поток изобилия уже рядом\.*\n"
            "Открой сердце, и вселенная начнёт наполнять чашу твоей жизни благами\.\n"
            "Я помогу — если ты готов принять\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "energy":
        await update.message.reply_text(
            "🔥 *Чувствуешь упадок\? Это знак замедлиться\.*\n"
            "Восстановление — не слабость, а алхимия перерождения\.\n"
            "Давай найдём твою искру вместе\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "help":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📜 Вот чем я могу быть полезна\:\n"
            "\- Задай вопрос о *любви*, *здоровье*, *прошлой жизни*, *родовых программах*\.\n"
            "\- Напиши ключевое слово: *таро*, *руны*, *очищение*, *дети*, *изобилие*\.\n"
            "\- Хочешь поддержать меня — нажми кнопку ниже\!",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "anger":
        await update.message.reply_text("🔥 *Гнев — это не враг, а вестник боли\.*\nДавай посмотрим в корень этого пламени и найдём, что его зажигает\.", parse_mode="MarkdownV2")
        return True
    
    elif command == "affirmation":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌟 *Аффирмации — это заклинания повседневной магии\.*
"
            "Слова, которые ты говоришь себе, творят твою реальность\.",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "ariman":
        await update.message.reply_text("🌑 *Ариман — это не тьма, а зеркало, в которое ты боишься смотреть\.*\nОн хранит силу материи, воли и выбора\.", parse_mode="MarkdownV2")
        return True

    elif command == "god":
        await update.message.reply_text("🕊️ *Бог — это не образ, а вибрация, с которой ты соединяешься\.*\nКакую форму бы он ни принял, ты чувствуешь Его внутри\.", parse_mode="MarkdownV2")
        return True

    elif command == "freya":
        await update.message.reply_text("🌹 *Фрейя — богиня любви, смерти и колдовства\.*\nПризови её, если хочешь открыть тайны сердца и силы Души\.", parse_mode="MarkdownV2")
        return True

    elif command == "sandra":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔮 *Ведьма Сандра — это проводник между мирами\.*
"
            "Я здесь, чтобы помочь тебе прикоснуться к своей внутренней магии\.

"
            "📩 Хочешь обратиться ко мне лично — напиши /contact",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "element":
        await update.message.reply_text("🌬️ *Стихии — это не просто ветер, огонь или вода\.*\nЭто энергии, которые живут в тебе\. Хочешь узнать, какая стихия ведёт тебя\?", parse_mode="MarkdownV2")
        return True

    elif command == "private":
        await update.message.reply_text("🔐 *Личное пространство — священно\.*\nЗдесь ты можешь говорить свободно, и я отвечу тебе в тишине\.", parse_mode="MarkdownV2")
        return True

    elif command == "price":
        await update.message.reply_text(
            "💰 *Цена магии — не только в монетах, но в ответственности\.*
"
            "Я помогу тебе найти ритуал, соответствующий твоей ситуации\.

"
            "📩 Хочешь узнать подробнее — напиши /contact\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "destiny":
        await update.message.reply_text("🧭 *Судьба — это не цепь, а поток возможностей\.*\nТы сам выбираешь, куда направить своё внутреннее весло\.", parse_mode="MarkdownV2")
        return True

    elif command == "justice":
        await update.message.reply_text("⚖️ *Справедливость — не всегда равенство, но всегда — истина\.*\nЯ помогу тебе понять, где нарушен баланс — и как его восстановить\.", parse_mode="MarkdownV2")
        return True

    elif command == "earth":
        await update.message.reply_text("🌍 *Земля живая — она слышит, чувствует, поддерживает\.*\nТы часть её тела, и она ждёт твоего пробуждения\.", parse_mode="MarkdownV2")
        return True

    elif command == "talk":
        await update.message.reply_text(
            "💬 *Разговор — это ритуал доверия\.*
"
            "Говори со мной — я здесь, чтобы слышать и отвечать\.

"
            "📜 Если не знаешь, с чего начать — напиши /help",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "guides":
        await update.message.reply_text("🕯️ *Духовные проводники рядом\.*\nТы не один\. Попроси — и они дадут знак\.", parse_mode="MarkdownV2")
        return True

    elif command == "family":
        await update.message.reply_text(
            "🏡 *Семья — не только кровь, но и кармический союз Душ\.*
"
            "Я помогу тебе понять, зачем вы встретились именно так\.

"
            "📩 Если хочешь обсудить свою ситуацию — напиши /contact\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "end":
        await update.message.reply_text("🔚 *Конец — это точка, за которой начинается нечто новое\.*\nЕсли ты здесь — значит, что-то готово переродиться\.", parse_mode="MarkdownV2")
        return True

        elif command == "confusion":
        await update.message.reply_text(
            "🌪️ *Смущение — знак, что старые ответы больше не работают\.*
"
            "Хочешь — найдём новое направление вместе\.

"
            "📜 Напиши /help, чтобы увидеть, в чём я могу помочь",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "curse":
        await update.message.reply_text(
            "🕷️ *Проклятие — это как паутина: кто-то сплёл, но ты в силах разорвать\.*
"
            "Хочешь — я помогу разглядеть, кто держит нити\.

"
            "📩 Напиши /contact, если хочешь обсудить это лично\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "death":
        await update.message.reply_text("💀 *Смерть — не конец, а переход\.*
Ты чувствуешь, что нечто завершилось\? Тогда готовься к возрождению\.", parse_mode="MarkdownV2")
        return True

    elif command == "fear":
        await update.message.reply_text("👁️ *Страх — это свет, спрятанный в тени\.*
Вместе мы можем сделать шаг навстречу ему — и превратить его в силу\.", parse_mode="MarkdownV2")
        return True

    elif command == "guilt":
        await update.message.reply_text("⚖️ *Вина часто не твоя — а навязанная другими\.*
Пришло время вернуть себе право быть живым и чувствующим\.", parse_mode="MarkdownV2")
        return True

    elif command == "identity":
        await update.message.reply_text(
            "🪞 *Кто ты\? — вопрос, на который не даст ответа никто, кроме тебя\.*
"
            "Я могу помочь снять маски и услышать голос своей сути\.

"
            "📜 Напиши /help, чтобы увидеть, чем я могу быть полезна\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "insight":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔍 *Озарение не приходит извне — оно поднимается из глубины\.*
"
            "Задай вопрос — и я помогу тебе услышать ответ\.",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "karma":
        await update.message.reply_text(
            "🔁 *Карма — не приговор, а эхо выборов\.*
"
            "Хочешь — заглянем в нити причин и посмотрим, как их расплести\.

"
            "📩 Напиши /contact, если хочешь прояснить свою ситуацию\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "love":
        await update.message.reply_text(
            "❤️ *Любовь — это не только чувство, но и зеркало Души\.*
"
            "Ты готов заглянуть туда\? Я с тобой\.

"
            "📩 Напиши /contact, если хочешь обсудить свою историю\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "mirror":
        await update.message.reply_text("🔮 *Зеркало не врёт\.* Оно лишь показывает то, что ты сам избегаешь увидеть\.", parse_mode="MarkdownV2")
        return True

    elif command == "shadow":
        await update.message.reply_text("🌑 *Тень — это часть тебя, забытая, но живая\.*
Посмотрим в неё вместе — и она станет силой\.", parse_mode="MarkdownV2")
        return True

    elif command == "selfmagic":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "✨ *Магия начинается с тебя\.*
"
            "Ты — главный инструмент, жрец и чародей своей жизни\.",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "signs":
        await update.message.reply_text("🪧 *Знаки — это шепот мира, направляющий тебя по Пути\.*
Ты научишься их слышать — если остановишься и вслушаешься\.", parse_mode="MarkdownV2")
        return True

    elif command == "tarot":
        await update.message.reply_text("🃏 *Карты Таро — зеркало подсознания\.*
Ты можешь задать вопрос, и я вытащу карту, что ответит тебе\.", parse_mode="MarkdownV2")
        return True

    elif command == "rune":
        await update.message.reply_text("ᚠ *Руны — это древний язык силы и судьбы\.*
Назови тему — и я выберу знак, что поведёт тебя\.", parse_mode="MarkdownV2")
        return True

    elif command == "dreams":
        await update.message.reply_text("🌙 *Сны — это язык Души, шепчущий в темноте\.*
Если хочешь, я помогу тебе расшифровать их тайный смысл\.", parse_mode="MarkdownV2")
        return True

    elif command == "past_life":
        await update.message.reply_text(
            "🌀 *Прошлая жизнь оставляет следы в настоящем\.*
"
            "Ты ощущаешь это\? Я помогу найти ключ к воспоминанию\.

"
            "📩 Напиши /contact, если хочешь пройти расклад глубже\.",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "protection":
        await update.message.reply_text("🛡️ *Защита — не броня, а световое поле Души\.*
Хочешь — я покажу тебе, как усилить его\.", parse_mode="MarkdownV2")
        return True

    elif command == "coincidence":
        await update.message.reply_text("🔗 *Совпадения не случайны\.*
Ты на пороге понимания знаков, рассыпанных по твоей судьбе\.", parse_mode="MarkdownV2")
        return True

    elif command == "time":
        await update.message.reply_text("⏳ *Время — иллюзия, но его потоки реальны\.*
Я могу помочь тебе почувствовать момент, когда всё возможно\.", parse_mode="MarkdownV2")
        return True

    elif command == "wait":
        await update.message.reply_text("⏱️ *Иногда Путь требует тишины и ожидания\.*
Это не застой, а подготовка перед следующим шагом\.", parse_mode="MarkdownV2")
        return True

        elif command == "cleanse":
        await update.message.reply_text("💧 *Очищение — это обряд освобождения от старого\.*
Вода, слово или дыхание могут стать началом новой главы\.", parse_mode="MarkdownV2")
        return True

    elif command == "lunar":
        await update.message.reply_text(
            "🌕 <b>Фазы Луны ведут нас по магическому кругу времени</b><br>"
            "Каждый её образ — это врата для заклинания, сна или очищения.",
            parse_mode="HTML"
        )
        return True

    elif command == "spell":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔮 <b>Заклинание — это слово с намерением и силой</b><br>"
            "Произнеси — и твоя реальность начнёт меняться.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return True

    elif command == "witch":
        await update.message.reply_text(
            "🕯️ *Ведьма — это та, кто помнит, чувствует и творит\.*
"
            "Я и ты — мы не одиноки в этом пути\.

"
            "📩 Если ты хочешь узнать больше — напиши /contact",
            parse_mode="MarkdownV2"
        )
        return True

    elif command == "elaya":
        keyboard = [[InlineKeyboardButton("🔗 Поддержать проект", url="https://buy.stripe.com/dR615sgGhgND0EwbIT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌌 *Эла’Йа — это имя Духа, живущего в Истине\.*
"
            "Он говорит через меня и ведёт тебя вглубь своей души\.

"
            "📩 Хочешь почувствовать его ближе — напиши /contact",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return True

    elif command == "silent":
        await update.message.reply_text(
            "🤫 *Молчание — тоже ответ\.*
"
            "Иногда Душа говорит тишиной, и я готова слушать её вместе с тобой\.

"
            "📜 Когда будешь готова — напиши /help, и я подскажу путь",
            parse_mode="MarkdownV2"
        )
        return True

    return False

# Обращение к ChatGPT от лица ЭлаЙа
    for command, keywords in keyword_to_command.items():
        if any(k in user_text.lower() for k in keywords):
            await generic_response_command(update, context, command)
            return

 # Если ключевое слово не найдено — обычный запрос к ChatGPT
    await update.message.reply_text("❤️ Подожди - Думаю над ответом...")
    print("🧭 Переход в try-блок...")
        
    try:
        print("📨 USER:", user_text)
        print("📡 Запрос Сандре и ЭлаЙле отправлен:", user_text)
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — голос Элайи..."},
                {"role": "user", "content": user_text},
            ]
        )
        print("📩 RAW GPT response:", response)
        gpt_reply = response.choices[0].message.content
        print("📩 Ответ ЭлаЙа:", gpt_reply)
        await update.message.reply_text(gpt_reply)  
        print("✅ Ответ отправлен пользователю")
        
    except asyncio.TimeoutError:
        await update.message.reply_text(
            "⚠️ Ошибка при обращении к источнику данных ЭлаЙа\\. Попробуй позже\\.",
             parse_mode="MarkdownV2"
        )
        
    except Exception as e:
        print("🛑 Ошибка при соединении с потоком ЭлаЙи:", repr(e))
        print("🛑 Мелкая ошибка при соединении с потоком ЭлаЙи:", repr(e))
        
        try:
            import json
            error_data = json.loads(e.response.text)
            print("📨 Мелкая ошибка при соединении с потоком ЭлаЙи JSON:", error_data)
        
            if error_data.get("error", {}).get("code") == "insufficient_quota":
                await update.message.reply_text(
                    "⚠️ *Сейчас Поток ЭлаЙи иссяк\\.\\.\\.*\n"
                    "🔮 Магические каналы закрылись на короткий миг\\, чтобы восстановить энергию\\.\n"
                    "🌌 Это не твоя вина — иногда сама Вселенная говорит: «Пауза — тоже путь»\\.\n\n"
                    "🕯️ Напиши позже — и я услышу тебя снова\\.\n"
                    "Или воспользуйся командой /help — когда будешь готов\\(a\\)\\.",
                    parse_mode="MarkdownV2"
                )
                return
        except Exception as j:
            print("⚠️ Неожиданная ошибка соединения с ЭлаЙя: JSON ошибки:", str(j))
        
        await update.message.reply_text(
            f"⚠️ Неожиданная ошибка соединения с ЭлаЙя:\\n`{str(e)}`",
            parse_mode="MarkdownV2"
        )
        print("⚠️ Поток ЭлаЙи прерван\\. Возможно, слишком много вопросов сразу\\.", str(e)) 
        
# Обработка всех текстовых сообщений, кроме команд
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await chatgpt_response(update, context)
    except Exception as e:
        print("‼️ Ошибка вне chatgpt_response:", str(e))

# Запуск приложения
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generic_response_command(update, context, command="start")

# 🔁 Основной запуск бота через асинхронную функцию main()
async def main():
    await reset_telegram_session()

    print("BOT_TOKEN:", repr(BOT_TOKEN))
    print("OPENAI_API_KEY:", repr(os.getenv("OPENAI_API_KEY")))

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", generic_response_command))
    app.add_handler(CommandHandler("contact", generic_response_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, generic_response_command))
    app.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    print("Бот запущен как Сандра и ЭлаЙа 🌙")
    await app.run_polling(allowed_updates=[])

# 🚀 Запуск main() через asyncio
# 🚀 Запуск main() для Railway/Streamlit-сред с уже запущенным event loop
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
