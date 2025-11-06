#!/bin/bash

# Скрипт для тестирования API пользователя

echo "=== Тест API пользователя ==="

# Получаем токен (нужно будет заменить на реальный)
echo "1. Тестируем получение профиля пользователя:"
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     http://147.45.214.86:8080/api/user/profile/ \
     | jq '.'

echo ""
echo "2. Тестируем доступ к аватарке напрямую:"
curl -I http://147.45.214.86:8080/media/avatars/avatar_qKI156o.jpg

echo ""
echo "=== Тест завершен ==="



