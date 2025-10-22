#!/bin/bash

# Скрипт для тестирования API профиля пользователя

echo "=== Тест API профиля пользователя ==="

# Получаем токен из базы данных (временное решение для тестирования)
echo "1. Получаем токен пользователя из базы данных:"
TOKEN=$(docker-compose exec web python manage.py shell -c "
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
user = User.objects.get(username='user_77088043414')
refresh = RefreshToken.for_user(user)
print(refresh.access_token)
" | tail -1)

echo "Токен: $TOKEN"

echo ""
echo "2. Тестируем получение профиля пользователя:"
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://147.45.214.86:8080/api/user/profile/ \
     | jq '.'

echo ""
echo "3. Проверяем, что возвращается в поле avatar_url:"
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://147.45.214.86:8080/api/user/profile/ \
     | jq '.avatar_url'

echo ""
echo "=== Тест завершен ==="
