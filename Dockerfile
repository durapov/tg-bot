FROM python:3.12-slim

WORKDIR /app

# Установка poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY poetry.lock pyproject.toml /app/

# Устанавливаем build-essential и зависимости poetry в одном RUN
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

# Копируем остальной исходный код
COPY . /app/

# Команда запуска
CMD ["python", "tg_bot/bot-aiogram.py"]
