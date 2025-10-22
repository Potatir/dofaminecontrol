#!/bin/bash

# Скрипт для исправления прав доступа к медиа файлам

echo "Проверяем и создаем необходимые папки..."

# Создаем папки если их нет
mkdir -p ./media/avatars
mkdir -p ./staticfiles

# Устанавливаем правильные права доступа
chmod -R 755 ./media
chmod -R 755 ./staticfiles

# Проверяем содержимое папки media
echo "Содержимое папки media:"
ls -la ./media/

echo "Содержимое папки media/avatars:"
ls -la ./media/avatars/

echo "Проверка завершена!"
