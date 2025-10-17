# 🚀 Руководство по развертыванию Dofamine Server

## 📋 Предварительные требования

### На сервере должно быть установлено:
- **Ubuntu 20.04+** или **CentOS 8+**
- **Docker** и **Docker Compose**
- **PostgreSQL** (если не используете Docker)
- **Nginx** (опционально, для продакшена)

### На локальной машине:
- **SSH доступ** к серверу
- **rsync** для копирования файлов

## 🔧 Быстрый деплой

### 1. Подготовка сервера
```bash
# Подключитесь к серверу
ssh root@YOUR_SERVER_IP

# Обновите систему
apt update && apt upgrade -y

# Установите необходимые пакеты
apt install -y curl wget rsync
```

### 2. Запуск деплоя
```bash
# Из локальной директории server/
chmod +x deploy_production.sh
./deploy_production.sh YOUR_SERVER_IP your-domain.com
```

### 3. Ручной деплой (если скрипт не работает)

#### Копирование файлов:
```bash
rsync -avz --exclude='.git' --exclude='__pycache__' \
    ./ root@YOUR_SERVER_IP:/opt/dofamine/
```

#### На сервере:
```bash
cd /opt/dofamine

# Настройте переменные окружения
cp production.env .env
nano .env  # Отредактируйте настройки

# Запустите контейнеры
docker-compose up -d --build

# Выполните миграции
docker-compose exec web python manage.py migrate

# Соберите статические файлы
docker-compose exec web python manage.py collectstatic --noinput

# Создайте суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## ⚙️ Конфигурация

### Переменные окружения (.env):
```env
# Обязательные
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,IP_ADDRESS
DB_PASSWORD=strong-password

# API ключи
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### Nginx конфигурация:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔍 Проверка деплоя

### 1. Проверка сервисов:
```bash
docker-compose ps
curl http://YOUR_SERVER_IP:8080/health/
```

### 2. Проверка API:
```bash
curl http://YOUR_SERVER_IP:8080/api/auth/me/
```

### 3. Проверка админ панели:
Откройте: `http://YOUR_SERVER_IP:8080/admin/`

## 🛠️ Управление сервисом

### Запуск/остановка:
```bash
docker-compose up -d    # Запуск
docker-compose down     # Остановка
docker-compose restart  # Перезапуск
```

### Логи:
```bash
docker-compose logs -f web    # Логи Django
docker-compose logs -f db     # Логи PostgreSQL
docker-compose logs -f nginx  # Логи Nginx
```

### Обновление:
```bash
git pull
docker-compose down
docker-compose up -d --build
```

## 🔒 Безопасность

### 1. Firewall:
```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 2. SSL сертификат (Let's Encrypt):
```bash
apt install certbot
certbot --nginx -d your-domain.com
```

### 3. Резервное копирование:
```bash
# База данных
docker-compose exec db pg_dump -U dofamine_user dofamine > backup.sql

# Медиа файлы
tar -czf media_backup.tar.gz /var/www/dofamine/media/
```

## 📊 Мониторинг

### Системные ресурсы:
```bash
htop
df -h
docker stats
```

### Логи приложения:
```bash
tail -f /opt/dofamine/logs/django.log
```

## 🆘 Устранение неполадок

### Проблема: Контейнеры не запускаются
```bash
docker-compose logs
docker-compose down
docker-compose up -d --build
```

### Проблема: База данных недоступна
```bash
docker-compose exec db psql -U dofamine_user -d dofamine
```

### Проблема: Статические файлы не загружаются
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Проверьте статус: `docker-compose ps`
3. Проверьте конфигурацию: `docker-compose config`
