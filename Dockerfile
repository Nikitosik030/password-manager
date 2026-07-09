FROM python:3.11-slim

WORKDIR /app

# Установка только CLI зависимостей (без tkinter)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY data/ ./data/

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Точка входа - CLI версия
ENTRYPOINT ["python", "-c", "from src.cli import cli; cli()"]