import asyncio
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def test():
    print("📡 Запрос к OpenAI...")
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты — голос Элайи"},
            {"role": "user", "content": "Что ты думаешь о душе?"},
        ]
    )
    print("📩 Ответ:", response.choices[0].message.content.strip())

asyncio.run(test())
