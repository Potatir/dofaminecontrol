#!/bin/bash

# Тест для проверки маршрутизации запросов

echo "=== Тест маршрутизации запросов ==="

echo "1. Тест прямого доступа к Django (порт 8000):"
curl -I http://localhost:8000/media/avatars/avatar_qKI156o.jpg

echo ""
echo "2. Тест через nginx (порт 8080):"
curl -I http://localhost:8080/media/avatars/avatar_qKI156o.jpg

echo ""
echo "3. Проверяем, какие порты открыты:"
netstat -tlnp | grep -E ':(8000|8080)'

echo ""
echo "4. Проверяем конфигурацию nginx:"
docker-compose exec nginx nginx -t

echo ""
echo "=== Тест завершен ==="
