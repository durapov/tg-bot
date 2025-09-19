import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Импортируем наш логгер
from user_logger import (
    log_command, 
    log_text_message, 
    log_unknown_command,
    log_bot_start,
    log_bot_stop,
    log_bot_error
)

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
    try:
        # Логируем команду
        log_command(message, "/start")
        
        await message.answer("Привет! Посмотри мои функции /help")
        print("Обработана команда /start")
        
    except Exception as e:
        log_bot_error(f"Ошибка в обработчике /start: {e}", message.from_user.id)
        await message.answer("Произошла ошибка. Попробуйте позже.")

# Обработчик команды /help
@dp.message(Command("help"))
async def bot_help_handler(message: Message):
    try:
        # Логируем команду
        log_command(message, "/help")
        
        await message.answer(
            "Известные мне команды:\n"
            "/help - помощь\n"
            "/start - запустить бота\n"
            "/stats - статистика логов (для админа)\n"
        )
        print("Обработана команда /help")
        
    except Exception as e:
        log_bot_error(f"Ошибка в обработчике /help: {e}", message.from_user.id)
        await message.answer("Произошла ошибка. Попробуйте позже.")

# Обработчик команды /stats (для админа)
@dp.message(Command("stats"))
async def bot_stats_handler(message: Message):
    try:
        # Проверяем, является ли пользователь админом (замените на свой ID)
        ADMIN_ID = 123456789  # Замените на свой Telegram ID
        
        if message.from_user.id != ADMIN_ID:
            log_command(message, "/stats")
            await message.answer("У вас нет прав для выполнения этой команды.")
            return
        
        # Логируем команду
        log_command(message, "/stats")
        
        # Импортируем логгер для получения статистики
        from user_logger import user_logger
        
        stats = user_logger.get_logs_statistics()
        
        if stats:
            stats_text = "📊 Статистика логов:\n\n"
            for filename, info in stats.items():
                stats_text += f"📄 {filename}\n"
                stats_text += f"   Размер: {info['size_mb']} MB\n"
                stats_text += f"   Изменен: {info['modified']}\n\n"
        else:
            stats_text = "Статистика логов недоступна."
        
        await message.answer(stats_text)
        
    except Exception as e:
        log_bot_error(f"Ошибка в обработчике /stats: {e}", message.from_user.id)
        await message.answer("Произошла ошибка при получении статистики.")

# Обработчик для всех остальных сообщений
@dp.message()
async def unknown_handler(message: Message):
    try:
        if message.text.startswith('/'):
            # Логируем неизвестную команду
            log_unknown_command(message, message.text)
            unknown_reply = "Неизвестная команда. Подробнее в /help"
        else:
            # Логируем текстовое сообщение
            log_text_message(message, message.text)
            unknown_reply = "Я пока не отвечаю на текстовые сообщения. Используйте команды. Подробнее в /help"
        
        await message.answer(unknown_reply)
        print(f"Неизвестное сообщение: {message.text}")
        
    except Exception as e:
        log_bot_error(f"Ошибка в обработчике неизвестных сообщений: {e}", 
                     message.from_user.id if message.from_user else None)

# Основная функция запуска бота
async def main():
    try:
        # Логируем запуск бота
        log_bot_start()
        print('Бот запущен')
        
        # Запускаем поллинг
        await dp.start_polling(bot)
        
    except Exception as e:
        log_bot_error(f"Критическая ошибка при запуске бота: {e}")
        print(f"Ошибка запуска: {e}")
    finally:
        # Логируем остановку бота
        log_bot_stop()
        print('Бот остановлен')

if __name__ == "__main__":
    asyncio.run(main())