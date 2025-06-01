import asyncio
import openai
import os
import sys  # вот эта строка важна

openai.api_key = os.getenv("OPENAI_API_KEY")

async def test():
    print("📡 Запрос к OpenAI...", file=sys.stderr)
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты — голос Элайи"},
            {"role": "user", "content": "Что ты думаешь о душе?"},
        ]
    )
    print("📩 Ответ:", response.choices[0].message.content.strip(), file=sys.stderr)

asyncio.run(test())

