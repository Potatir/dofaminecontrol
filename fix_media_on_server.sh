#!/bin/bash

# Скрипт для исправления прав доступа к медиа файлам на сервере

echo "=== Исправление прав доступа к медиа файлам ==="

# Создаем папки если их нет
echo "Создаем необходимые папки..."
mkdir -p ./media/avatars
mkdir -p ./staticfiles

# Устанавливаем правильные права доступа
echo "Устанавливаем права доступа..."
chmod -R 755 ./media
chmod -R 755 ./staticfiles

# Проверяем содержимое папки media
echo ""
echo "Содержимое папки media:"
ls -la ./media/

echo ""
echo "Содержимое папки media/avatars:"
ls -la ./media/avatars/

# Запускаем Django команду для проверки медиа файлов
echo ""
echo "Запускаем проверку медиа файлов через Django..."
docker-compose exec web python manage.py check_media

echo ""
echo "=== Исправление завершено ==="

