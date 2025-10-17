# Dockerfile для Dofamine Server

FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Создание директорий для статических файлов и медиа
RUN mkdir -p /app/staticfiles /app/media

# Настройка переменных окружения
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=core.settings

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]


