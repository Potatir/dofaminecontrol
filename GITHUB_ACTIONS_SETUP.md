# Настройка GitHub Actions для автоматического развертывания

## 1. Настройка Secrets в GitHub

Перейдите в ваш репозиторий на GitHub: https://github.com/Potatir/dofaminecontrol

### Добавьте следующие Secrets:

1. **Перейдите в Settings → Secrets and variables → Actions**
2. **Нажмите "New repository secret"**
3. **Добавьте следующие секреты:**

#### `SERVER_HOST`
- **Name:** `SERVER_HOST`
- **Value:** IP адрес вашего сервера (например: `123.456.789.0`)

#### `SERVER_USER`
- **Name:** `SERVER_USER`
- **Value:** Имя пользователя для SSH подключения (например: `root` или `ubuntu`)

#### `SERVER_SSH_KEY`
- **Name:** `SERVER_SSH_KEY`
- **Value:** Приватный SSH ключ для доступа к серверу

## 2. Создание SSH ключа для сервера

### На вашем компьютере выполните:
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions@dofamine"
```

### Скопируйте публичный ключ на сервер:
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub root@YOUR_SERVER_IP
```

### Или вручную:
1. Скопируйте содержимое `~/.ssh/id_rsa.pub`
2. На сервере выполните:
```bash
mkdir -p ~/.ssh
echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

## 3. Подготовка сервера

### Установите Docker и Docker Compose:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Создайте директорию для проекта:
```bash
mkdir -p /opt/dofamine-server
cd /opt/dofamine-server
git clone https://github.com/Potatir/dofaminecontrol.git .
```

### Создайте файл .env на сервере:
```bash
nano /opt/dofamine-server/.env
```

Добавьте в файл:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dofamine
DB_USER=dofamine_user
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_HOST=db
DB_PORT=5432
SECRET_KEY=YOUR_SECRET_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.com,YOUR_SERVER_IP
```

## 4. Запуск первого развертывания

### На сервере выполните:
```bash
cd /opt/dofamine-server
docker-compose up -d
```

### Проверьте статус:
```bash
docker-compose ps
docker-compose logs
```

## 5. Настройка домена (опционально)

### Если у вас есть домен:
1. Настройте DNS записи на ваш сервер
2. Обновите `ALLOWED_HOSTS` в .env файле
3. Настройте SSL сертификаты в nginx.conf

## 6. Проверка работы

После настройки:
1. Сделайте любой коммит в main ветку
2. GitHub Actions автоматически запустит пайплайн
3. Проверьте логи в Actions вкладке
4. Ваш сервер должен обновиться автоматически

## 7. Мониторинг

### Полезные команды на сервере:
```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs web

# Логи базы данных
docker-compose logs db

# Перезапуск сервисов
docker-compose restart

# Обновление и перезапуск
docker-compose pull && docker-compose up -d
```
