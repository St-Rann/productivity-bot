import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "7689103224:AAGCIQeUGLUdXrEFGtweIkJSaSm8aXFD8EI"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    await message.reply("Привет! Я Productivity Coach. Задай мне любой вопрос или напиши задачу!")

@dp.message_handler(commands=['addtask'])
async def add_task(message: Message):
    task = message.get_args()
    if not task:
        await message.reply("Пожалуйста, укажи задачу после команды /addtask.")
    else:
        await message.reply(f"Задача добавлена: {task}")

@dp.message_handler()
async def handle_message(message: Message):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        answer = response.choices[0].message.content.strip()
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
