import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import FastAPI, Request
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
router = Router()
dp.include_router(router)
app = FastAPI()
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
db = sqlite3.connect("bot.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (user_id INTEGER, task TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS logs (user_id INTEGER, command TEXT)")

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    db.commit()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Donate ☕", url="https://buymeacoffee.com/yourpage")]
    ])
    await message.answer("Hi! I’m your Productivity Coach bot ☀️\nUse /addtask, /mytasks, /done, or just chat with me!", reply_markup=kb)

@router.message(Command("addtask"))
async def cmd_addtask(message: Message):
    cursor.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (message.from_user.id, message.text.replace("/addtask ", "")))
    db.commit()
    cursor.execute("INSERT INTO logs (user_id, command) VALUES (?, ?)", (message.from_user.id, "addtask"))
    db.commit()
    await message.answer("✅ Task added!")

@router.message(Command("mytasks"))
async def cmd_mytasks(message: Message):
    cursor.execute("SELECT task FROM tasks WHERE user_id=?", (message.from_user.id,))
    tasks = cursor.fetchall()
    task_list = "\n".join([f"• {t[0]}" for t in tasks]) or "No tasks yet."
    await message.answer(f"📋 Your tasks:\n{task_list}")

@router.message(Command("done"))
async def cmd_done(message: Message):
    cursor.execute("DELETE FROM tasks WHERE user_id=? AND task=?", (message.from_user.id, message.text.replace("/done ", "")))
    db.commit()
    await message.answer("✅ Task marked as done!")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (message.from_user.id,))
    tasks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM logs WHERE user_id=?", (message.from_user.id,))
    cmds = cursor.fetchone()[0]
    await message.answer(f"📊 You have {tasks} tasks and used {cmds} commands.")

@router.message(Command("donate"))
async def cmd_donate(message: Message):
    await message.answer("Support the bot here: https://buymeacoffee.com/yourpage")

@router.message(F.text)
async def chat_handler(message: Message):
    cursor.execute("INSERT INTO logs (user_id, command) VALUES (?, ?)", (message.from_user.id, "chat"))
    db.commit()
    prompt = f"You are a productivity coach. Help the user:\nUser: {message.text}\nCoach:"
    try:
        response = await openai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo"
        )
        reply = response.choices[0].message.content.strip()
        await message.answer(reply)
    except Exception:
        await message.answer("⚠️ Sorry, I couldn't process that right now. Try again later.")

@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return {"ok": True}

async def on_startup():
    webhook_url = "https://your-domain.com/webhook"
    await bot.set_webhook(webhook_url)

if __name__ == "__main__":
    import uvicorn
    asyncio.get_event_loop().run_until_complete(on_startup())
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
