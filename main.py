
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import FastAPI
from openai import AsyncOpenAI
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я готов помочь тебе быть продуктивнее!")

@dp.message(Command("addtask"))
async def cmd_addtask(message: types.Message):
    await message.answer("Какую задачу добавить?")

@dp.message()
async def handle_message(message: types.Message):
    response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.text}]
    )
    answer = response.choices[0].message.content.strip()
    await message.answer(answer)

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://web-production-0d58.up.railway.app/webhook"
    await bot.set_webhook(webhook_url)

@app.post("/webhook")
async def process_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    asyncio.get_event_loop().run_until_complete(on_startup())
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
