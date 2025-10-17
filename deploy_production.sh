#!/bin/bash

# Скрипт для развертывания Dofamine Server в продакшене
# Использование: ./deploy_production.sh [HOST_IP] [DOMAIN]

set -e

HOST_IP=${1:-"your-server-ip"}
DOMAIN=${2:-"your-domain.com"}

echo "🚀 Начинаем развертывание Dofamine Server в продакшене..."
echo "📍 Хост: $HOST_IP"
echo "🌐 Домен: $DOMAIN"

# Проверяем подключение к серверу
echo "🔍 Проверяем подключение к серверу..."
if ! ping -c 1 $HOST_IP > /dev/null 2>&1; then
    echo "❌ Ошибка: Не удается подключиться к серверу $HOST_IP"
    exit 1
fi

# Копируем файлы на сервер
echo "📤 Копируем файлы на сервер..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='db.sqlite3' \
    ./ root@$HOST_IP:/opt/dofamine/

# Подключаемся к серверу и выполняем деплой
echo "🔧 Выполняем деплой на сервере..."
ssh root@$HOST_IP << EOF
    cd /opt/dofamine
    
    # Обновляем конфигурацию
    sed -i "s/your-domain.com/$DOMAIN/g" production.env
    sed -i "s/IP_ADDRESS/$HOST_IP/g" production.env
    
    # Устанавливаем Docker и Docker Compose
    if ! command -v docker &> /dev/null; then
        echo "📦 Устанавливаем Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl start docker
        systemctl enable docker
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "📦 Устанавливаем Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Создаем директории
    mkdir -p /var/www/dofamine/{media,static}
    mkdir -p /opt/dofamine/logs
    
    # Запускаем сервисы
    echo "🐳 Запускаем Docker контейнеры..."
    docker-compose -f docker-compose.yml --env-file production.env up -d --build
    
    # Ждем запуска базы данных
    echo "⏳ Ждем запуска базы данных..."
    sleep 30
    
    # Выполняем миграции
    echo "🗄️ Выполняем миграции..."
    docker-compose exec -T web python manage.py migrate
    
    # Собираем статические файлы
    echo "📄 Собираем статические файлы..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    # Создаем суперпользователя
    echo "👤 Создаем суперпользователя..."
    docker-compose exec -T web python manage.py createsuperuser --noinput || echo "Суперпользователь уже существует"
    
    # Проверяем статус
    echo "✅ Проверяем статус сервисов..."
    docker-compose ps
    
    echo "🎉 Деплой завершен!"
    echo "🌐 Сервер доступен по адресу: http://$HOST_IP:8080"
    echo "📊 Админ панель: http://$HOST_IP:8080/admin/"
EOF

echo "✅ Деплой завершен успешно!"
echo "🌐 Ваш сервер доступен по адресу: http://$HOST_IP:8080"
echo "📊 Админ панель: http://$HOST_IP:8080/admin/"
echo ""
echo "📋 Следующие шаги:"
echo "1. Обновите DNS записи для вашего домена"
echo "2. Настройте SSL сертификат (Let's Encrypt)"
echo "3. Обновите AppConfig в Flutter приложении"
echo "4. Протестируйте API endpoints"
