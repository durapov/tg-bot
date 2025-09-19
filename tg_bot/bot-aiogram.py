import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем значения переменных из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start


@dp.message(Command("start"))
async def bot_start_handler(message: Message):
    await message.answer("Привет! Посмотри мои функции /help")
    print("Обработана команда /start")

# Обработчик команды /help


@dp.message(Command("help"))
async def bot_help_handler(message: Message):
    await message.answer(
        "Известные мне команды:\n"
        "/help - помощь\n"
        "/start - запустить бота\n"
    )
    print("Обработана команда /help")

# Обработчик для всех остальных сообщений


@dp.message()
async def unknown_handler(message: Message):
    if message.text.startswith('/'):
        unknown_reply = "Неизвестная команда. Подробнее в /help"
    else:
        unknown_reply = "Я пока не отвечаю на текстовые сообщения. Используйте команды. Подробнее в /help"

    await message.answer(unknown_reply)
    print(f"Неизвестное сообщение: {message.text}")

# Основная функция запуска бота


async def main():
    print('Бот запущен')
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
