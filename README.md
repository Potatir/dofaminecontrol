# 🧠 Dofamine Server

Django REST API для мобильного приложения Dofamine - приложения для контроля зависимостей и развития полезных привычек.

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/dofamine-server.git
cd dofamine-server
```

### 2. Настройка окружения
```bash
# Скопируйте файл конфигурации
cp production.env .env

# Отредактируйте настройки
nano .env
```

### 3. Запуск с Docker
```bash
# Запуск всех сервисов
docker-compose up -d

# Выполнение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## 📋 API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/token/` - Получение JWT токена
- `POST /api/auth/sms/send/` - Отправка SMS кода
- `POST /api/auth/sms/verify/` - Проверка SMS кода

### Пользователи
- `GET /api/auth/me/` - Информация о пользователе
- `PUT /api/user/profile/` - Обновление профиля
- `POST /api/user/avatar/` - Загрузка аватара

### Привычки
- `GET /api/habits/` - Список привычек
- `POST /api/habits/` - Создание привычки
- `PUT /api/habits/{id}/` - Обновление привычки

### Чат с ИИ
- `GET /api/chat/sessions/` - Список сессий
- `POST /api/chat/sessions/` - Создание сессии
- `POST /api/chat/sessions/{id}/send/` - Отправка сообщения

## 🛠️ Технологии

- **Django 4.2.7** - Web framework
- **Django REST Framework** - API
- **PostgreSQL** - База данных
- **Redis** - Кеширование
- **Docker** - Контейнеризация
- **Nginx** - Веб-сервер
- **Twilio** - SMS аутентификация
- **OpenAI** - ИИ чат

## 🔧 Конфигурация

### Обязательные переменные окружения:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_PASSWORD=strong-password
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

## 📦 Деплой

### Автоматический деплой с GitHub:
```bash
chmod +x deploy_from_github.sh
./deploy_from_github.sh your-username/dofamine-server main your-server-ip your-domain.com
```

### Ручной деплой:
1. Клонируйте репозиторий на сервер
2. Настройте `.env` файл
3. Запустите `docker-compose up -d`
4. Выполните миграции

## 📊 Мониторинг

- **Логи:** `docker-compose logs -f`
- **Статус:** `docker-compose ps`
- **Админ панель:** `http://your-domain.com/admin/`

## 🤝 Разработка

### Установка зависимостей:
```bash
pip install -r requirements.txt
```

### Запуск в режиме разработки:
```bash
python manage.py runserver
```

### Выполнение тестов:
```bash
python manage.py test
```

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)