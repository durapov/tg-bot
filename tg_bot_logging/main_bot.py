import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Импортируем функции логирования
from user_logger import (
    log_command, 
    log_text_message, 
    log_unknown_command,
    log_bot_started,
    log_bot_stopped,
    log_error,
    get_stats
)

# Загружаем переменные из файла .env
load_dotenv()

# Получаем значения переменных из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ID админа из .env

# Настраиваем базовое логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: Message):
    log_command(message, "/start")
    await message.answer("Привет! Посмотри мои функции /help")


@dp.message(Command("help"))
async def help_handler(message: Message):
    log_command(message, "/help")
    await message.answer(
        "Известные мне команды:\n"
        "/help - помощь\n"
        "/start - запустить бота\n"
        "/stats - статистика (только для админа)\n"
    )


@dp.message(Command("stats"))
async def stats_handler(message: Message):
    log_command(message, "/stats")
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        stats = get_stats()
        if stats:
            stats_text = "📊 Статистика логов:\n\n"
            for filename, info in stats.items():
                stats_text += f"📄 {filename}\n"
                stats_text += f"   Размер: {info['size_mb']} MB\n"
                stats_text += f"   Изменен: {info['modified'][:19]}\n\n"
            await message.answer(stats_text)
        else:
            await message.answer("Статистика недоступна.")
    except Exception as e:
        log_error(f"Ошибка при получении статистики: {e}", message.from_user.id)
        await message.answer("Ошибка при получении статистики.")


@dp.message()
async def unknown_handler(message: Message):
    if message.text.startswith('/'):
        log_unknown_command(message)
        await message.answer("Неизвестная команда. Подробнее в /help")
    else:
        log_text_message(message)
        await message.answer("Я пока не отвечаю на текстовые сообщения. Используйте команды.")


async def main():
    try:
        log_bot_started()
        print('Бот запущен')
        await dp.start_polling(bot)
    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        print(f"Ошибка: {e}")
    finally:
        log_bot_stopped()


if __name__ == "__main__":
    asyncio.run(main())