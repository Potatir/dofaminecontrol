# Dofamine Server

Django REST API сервер для приложения Dofamine - приложения для контроля времени использования смартфона.

## Особенности

- Django REST Framework API
- PostgreSQL база данных
- Система аутентификации пользователей
- Управление подписками
- Система достижений
- AI чат интеграция
- Статистика использования приложений
- Timeline данных пользователей

## Требования

- Python 3.8+
- PostgreSQL 12+
- Redis (опционально, для кеширования)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd server
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

5. Выполните миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## Структура проекта

```
server/
├── accounts/          # Приложение для управления пользователями
├── core/             # Основные настройки Django
├── media/            # Загруженные пользователями файлы
├── requirements.txt  # Python зависимости
├── manage.py         # Django management script
└── README.md         # Этот файл
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/logout/` - Выход из системы

### Пользователи
- `GET /api/user/profile/` - Получить профиль пользователя
- `PUT /api/user/profile/` - Обновить профиль пользователя

### Приложения
- `GET /api/apps/` - Получить список приложений пользователя
- `POST /api/apps/` - Добавить приложение
- `PUT /api/apps/{id}/` - Обновить приложение

### Timeline
- `GET /api/timeline/` - Получить timeline данные
- `POST /api/timeline/` - Сохранить timeline данные

### Достижения
- `GET /api/achievements/` - Получить список достижений
- `POST /api/achievements/sync/` - Синхронизировать достижения

## Переменные окружения

Создайте файл `.env` на основе `env.example`:

- `DB_ENGINE` - Тип базы данных (по умолчанию PostgreSQL)
- `DB_NAME` - Имя базы данных
- `DB_USER` - Пользователь базы данных
- `DB_PASSWORD` - Пароль базы данных
- `DB_HOST` - Хост базы данных
- `DB_PORT` - Порт базы данных
- `SECRET_KEY` - Секретный ключ Django
- `DEBUG` - Режим отладки (True/False)
- `ALLOWED_HOSTS` - Разрешенные хосты

## Развертывание

### С Docker

```bash
docker-compose up -d
```

### На сервере

1. Установите зависимости сервера
2. Настройте PostgreSQL
3. Скопируйте переменные окружения
4. Выполните миграции
5. Соберите статические файлы: `python manage.py collectstatic`
6. Настройте веб-сервер (Nginx + Gunicorn)

## CI/CD

Проект настроен для автоматического развертывания через GitLab CI/CD. При пуше в ветку `main` автоматически запускается пайплайн развертывания.

## Лицензия

Private project - All rights reserved.
