import json
import os
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
from aiogram.types import Message, User


class UserActionLogger:
    def __init__(self, logs_dir: str = "logs"):
        """
        Инициализация логгера для действий пользователей
        
        Args:
            logs_dir: Директория для сохранения логов
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Настройка основного логгера для действий пользователей
        self.user_logger = self._setup_logger(
            name="user_actions",
            filename=self.logs_dir / "user_actions.log",
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5
        )
        
        # Логгер для системных событий
        self.system_logger = self._setup_logger(
            name="system_events", 
            filename=self.logs_dir / "system_events.log",
            max_bytes=5 * 1024 * 1024,  # 5MB
            backup_count=3
        )
        
        # Логгер для ошибок
        self.error_logger = self._setup_logger(
            name="bot_errors",
            filename=self.logs_dir / "bot_errors.log", 
            max_bytes=5 * 1024 * 1024,  # 5MB
            backup_count=3,
            level=logging.ERROR
        )

    def _setup_logger(self, name: str, filename: Path, max_bytes: int, 
                     backup_count: int, level: int = logging.INFO) -> logging.Logger:
        """
        Настройка отдельного логгера с JSON форматированием
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Убираем существующие обработчики
        logger.handlers.clear()
        
        # Создаем RotatingFileHandler
        handler = RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Устанавливаем кастомный форматтер
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False  # Не передаем в root logger
        
        return logger

    def log_user_action(self, message: Message, action_type: str, 
                       action_data: str, additional_data: Optional[Dict[str, Any]] = None):
        """
        Логирование действия пользователя
        
        Args:
            message: Объект сообщения от aiogram
            action_type: Тип действия (command, text_message, unknown_command)
            action_data: Данные действия (текст команды, сообщения)
            additional_data: Дополнительные данные для логирования
        """
        try:
            user_data = self._extract_user_data(message.from_user)
            chat_data = self._extract_chat_data(message)
            
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_type": action_type,
                "action_data": action_data,
                "message_id": message.message_id,
                **user_data,
                **chat_data
            }
            
            # Добавляем дополнительные данные если есть
            if additional_data:
                log_entry["additional_data"] = additional_data
            
            self.user_logger.info(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            self.error_logger.error(f"Ошибка при логировании действия пользователя: {e}")

    def log_system_event(self, event_type: str, event_data: str, 
                        additional_data: Optional[Dict[str, Any]] = None):
        """
        Логирование системного события
        
        Args:
            event_type: Тип события (bot_started, bot_stopped, error)
            event_data: Описание события
            additional_data: Дополнительные данные
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "event_data": event_data
            }
            
            if additional_data:
                log_entry["additional_data"] = additional_data
            
            self.system_logger.info(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            self.error_logger.error(f"Ошибка при логировании системного события: {e}")

    def log_error(self, error_type: str, error_message: str, 
                  user_id: Optional[int] = None, additional_data: Optional[Dict[str, Any]] = None):
        """
        Логирование ошибки
        
        Args:
            error_type: Тип ошибки
            error_message: Сообщение об ошибке
            user_id: ID пользователя (если ошибка связана с пользователем)
            additional_data: Дополнительные данные
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_type": error_type,
                "error_message": error_message
            }
            
            if user_id:
                log_entry["user_id"] = user_id
                
            if additional_data:
                log_entry["additional_data"] = additional_data
            
            self.error_logger.error(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            # Fallback логирование в случае критической ошибки
            print(f"Критическая ошибка логгера: {e}")

    def _extract_user_data(self, user: User) -> Dict[str, Any]:
        """Извлечение данных пользователя"""
        return {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "is_bot": user.is_bot,
            "is_premium": getattr(user, 'is_premium', None)
        }

    def _extract_chat_data(self, message: Message) -> Dict[str, Any]:
        """Извлечение данных чата"""
        return {
            "chat_id": message.chat.id,
            "chat_type": message.chat.type
        }

    def get_logs_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по логам
        
        Returns:
            Словарь с информацией о размерах файлов логов
        """
        try:
            stats = {}
            
            for log_file in self.logs_dir.glob("*.log"):
                if log_file.exists():
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    stats[log_file.name] = {
                        "size_mb": round(size_mb, 2),
                        "modified": datetime.fromtimestamp(
                            log_file.stat().st_mtime
                        ).isoformat()
                    }
            
            return stats
            
        except Exception as e:
            self.error_logger.error(f"Ошибка при получении статистики логов: {e}")
            return {}


class JSONFormatter(logging.Formatter):
    """
    Кастомный форматтер для JSON логов
    """
    def format(self, record):
        # Возвращаем только сообщение, так как оно уже в JSON формате
        return record.getMessage()


# Создаем глобальный экземпляр логгера
logger = UserActionLogger()


# API функции для использования в боте
def log_command(message: Message, command_name: str):
    """Логирование команды"""
    logger.log_user_action(message, "command", command_name)


def log_text_message(message: Message):
    """Логирование текстового сообщения"""
    logger.log_user_action(message, "text_message", message.text[:100])  # Ограничиваем длину


def log_unknown_command(message: Message):
    """Логирование неизвестной команды"""
    logger.log_user_action(message, "unknown_command", message.text)


def log_bot_started():
    """Логирование запуска бота"""
    logger.log_system_event("bot_started", "Бот успешно запущен")


def log_bot_stopped():
    """Логирование остановки бота"""
    logger.log_system_event("bot_stopped", "Бот остановлен")


def log_error(error_message: str, user_id: Optional[int] = None):
    """Логирование ошибки"""
    logger.log_error("bot_error", error_message, user_id)


def get_stats():
    """Получение статистики логов"""
    return logger.get_logs_statistics()