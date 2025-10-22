#!/bin/bash

# Скрипт для диагностики nginx и медиа файлов

echo "=== Диагностика nginx и медиа файлов ==="

echo "1. Проверяем содержимое папки media на хосте:"
ls -la ./media/avatars/ | head -10

echo ""
echo "2. Проверяем содержимое папки media в nginx контейнере:"
docker-compose exec nginx ls -la /var/www/media/avatars/ | head -10

echo ""
echo "3. Проверяем содержимое папки media в web контейнере:"
docker-compose exec web ls -la /app/media/avatars/ | head -10

echo ""
echo "4. Проверяем права доступа в nginx контейнере:"
docker-compose exec nginx ls -la /var/www/media/

echo ""
echo "5. Тестируем доступ к файлу через nginx:"
curl -I http://localhost:8080/media/avatars/avatar_qKI156o.jpg

echo ""
echo "=== Диагностика завершена ==="
