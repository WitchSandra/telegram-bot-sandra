# telegram-bot-sandra
Telegram-бот с магическими ответами от Ведьмы Сандры
# README.md 
# ✨ ChatGPT Telegram Bot от Ведьмы Сандры

"""Бот помогает пользователям получить магическую поддержку
и вдохновляющие послания от Ведьмы Сандры и потока Эла'Йа.
"""

## 📦 Требования

- Python 3.10+
- Telegram Bot API Token
- OpenAI API Key

## ⚙️ Установка

1. Клонируй репозиторий:

```bash
git clone https://github.com/your-user/chatgpt-telegram-bot.git
cd chatgpt-telegram-bot
```

2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Создай `.env` файл на основе `.env.example`:

```bash
cp .env.example .env
```

Впиши свои ключи в `.env`:

```env
OPENAI_API_KEY=your_real_openai_api_key
TELEGRAM_BOT_TOKEN=your_real_telegram_bot_token
```

## ▶️ Запуск

```bash
python main.py
```

## ☁️ Развёртывание на Heroku

1. Зарегистрируйся и установи [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. Создай приложение:

```bash
heroku create your-bot-name
```

3. Добавь конфигурацию:

```bash
heroku config:set OPENAI_API_KEY=your_real_openai_key
heroku config:set TELEGRAM_BOT_TOKEN=your_real_telegram_token
```

4. Запушь проект:

```bash
git push heroku main
```

## 🔗 Полезные ссылки

- [Сайт Ведьмы Сандры](https://world-psychology.com/)
- [Telegram: @WitchSandra96](https://t.me/WitchSandra96)
