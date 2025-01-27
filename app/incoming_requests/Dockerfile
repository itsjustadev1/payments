FROM python:3.11-slim

# Устанавливаем зависимости
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy[asyncio] asyncpg python-dotenv python-dateutil

# Копируем содержимое проекта в контейнер
WORKDIR /app
COPY . /app

# Открываем порт 8080 для приложения
EXPOSE 8080