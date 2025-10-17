#!/bin/bash

# Скрипт для развертывания Dofamine Server

set -e

echo "🚀 Начинаем развертывание Dofamine Server..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: manage.py не найден. Убедитесь, что вы в корневой директории проекта."
    exit 1
fi

# Создаем директории если их нет
echo "📁 Создаем необходимые директории..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt

# Выполняем миграции
echo "🗄️ Выполняем миграции базы данных..."
python manage.py migrate

# Собираем статические файлы
echo "📄 Собираем статические файлы..."
python manage.py collectstatic --noinput

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию Django..."
python manage.py check --deploy

# Создаем суперпользователя если его нет (только в продакшене)
if [ "$DJANGO_ENV" = "production" ] && [ ! -f "superuser_created.flag" ]; then
    echo "👤 Создаем суперпользователя..."
    python manage.py createsuperuser --noinput || echo "Суперпользователь уже существует"
    touch superuser_created.flag
fi

# Запускаем сервер
echo "✅ Развертывание завершено!"
echo "🌐 Запускаем сервер..."

if [ "$DJANGO_ENV" = "production" ]; then
    echo "🚀 Запуск в продакшен режиме с Gunicorn..."
    exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 core.wsgi:application
else
    echo "🔧 Запуск в режиме разработки..."
    exec python manage.py runserver 0.0.0.0:8000
fi


