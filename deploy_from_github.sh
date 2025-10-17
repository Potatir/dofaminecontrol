#!/bin/bash

# Скрипт для развертывания с GitHub
# Использование: ./deploy_from_github.sh [GITHUB_REPO] [BRANCH] [HOST_IP] [DOMAIN]

set -e

GITHUB_REPO=${1:-"your-username/dofamine-server"}
BRANCH=${2:-"main"}
HOST_IP=${3:-"your-server-ip"}
DOMAIN=${4:-"your-domain.com"}

echo "🚀 Начинаем развертывание Dofamine Server с GitHub..."
echo "📦 Репозиторий: $GITHUB_REPO"
echo "🌿 Ветка: $BRANCH"
echo "📍 Хост: $HOST_IP"
echo "🌐 Домен: $DOMAIN"

# Проверяем подключение к серверу
echo "🔍 Проверяем подключение к серверу..."
if ! ping -c 1 $HOST_IP > /dev/null 2>&1; then
    echo "❌ Ошибка: Не удается подключиться к серверу $HOST_IP"
    exit 1
fi

# Подключаемся к серверу и выполняем деплой
echo "🔧 Выполняем деплой на сервере..."
ssh root@$HOST_IP << EOF
    # Создаем директорию проекта
    mkdir -p /opt/dofamine
    cd /opt/dofamine
    
    # Клонируем или обновляем репозиторий
    if [ -d ".git" ]; then
        echo "📥 Обновляем существующий репозиторий..."
        git fetch origin
        git checkout $BRANCH
        git pull origin $BRANCH
    else
        echo "📥 Клонируем репозиторий..."
        git clone https://github.com/$GITHUB_REPO.git .
        git checkout $BRANCH
    fi
    
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
    
    # Создаем .env файл из production.env
    if [ ! -f ".env" ]; then
        echo "⚙️ Создаем конфигурацию..."
        cp production.env .env
        sed -i "s/your-domain.com/$DOMAIN/g" .env
        sed -i "s/IP_ADDRESS/$HOST_IP/g" .env
        echo "⚠️  ВАЖНО: Отредактируйте .env файл с вашими реальными настройками!"
        echo "   nano .env"
    fi
    
    # Создаем директории
    mkdir -p /var/www/dofamine/{media,static}
    mkdir -p logs
    
    # Останавливаем старые контейнеры
    echo "🛑 Останавливаем старые контейнеры..."
    docker-compose down || true
    
    # Запускаем новые контейнеры
    echo "🐳 Запускаем Docker контейнеры..."
    docker-compose up -d --build
    
    # Ждем запуска базы данных
    echo "⏳ Ждем запуска базы данных..."
    sleep 30
    
    # Выполняем миграции
    echo "🗄️ Выполняем миграции..."
    docker-compose exec -T web python manage.py migrate
    
    # Собираем статические файлы
    echo "📄 Собираем статические файлы..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    # Создаем суперпользователя (если не существует)
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
echo "1. Отредактируйте .env файл на сервере: ssh root@$HOST_IP 'nano /opt/dofamine/.env'"
echo "2. Обновите DNS записи для вашего домена"
echo "3. Настройте SSL сертификат (Let's Encrypt)"
echo "4. Обновите AppConfig в Flutter приложении"
