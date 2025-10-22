#!/bin/bash

# Скрипт для проверки логов и отладки аватарок

echo "=== Отладка аватарок ==="

echo "1. Проверяем логи Django:"
docker-compose logs web --tail=50 | grep -E "(avatar|profile|user)"

echo ""
echo "2. Проверяем логи nginx:"
docker-compose logs nginx --tail=20

echo ""
echo "3. Проверяем содержимое папки media:"
ls -la ./media/avatars/ | head -5

echo ""
echo "4. Тестируем доступ к аватарке:"
curl -I http://147.45.214.86:8080/media/avatars/avatar_qKI156o.jpg

echo ""
echo "5. Проверяем пользователей в базе данных:"
docker-compose exec web python manage.py shell -c "
from accounts.models import User
users = User.objects.filter(avatar__isnull=False).exclude(avatar='')
for user in users:
    print(f'User: {user.username}, Avatar: {user.avatar}, Avatar URL: {user.avatar.url}')
"

echo ""
echo "=== Отладка завершена ==="
