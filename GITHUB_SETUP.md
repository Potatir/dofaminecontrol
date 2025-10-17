# 📤 Загрузка на GitHub

## 1. Создание репозитория на GitHub

1. Зайдите на [GitHub.com](https://github.com)
2. Нажмите **"New repository"**
3. Заполните:
   - **Repository name:** `dofamine-server`
   - **Description:** `Django REST API for Dofamine mobile app`
   - **Visibility:** Private (рекомендуется)
   - **Initialize:** НЕ ставьте галочки (у нас уже есть код)

## 2. Инициализация Git в проекте

```bash
cd C:\dofamine\server

# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Django REST API for Dofamine"

# Добавление удаленного репозитория
git remote add origin https://github.com/YOUR_USERNAME/dofamine-server.git

# Загрузка на GitHub
git push -u origin main
```

## 3. Настройка .gitignore

Убедитесь, что файл `.gitignore` содержит:
- `.env` файлы
- `db.sqlite3`
- `__pycache__/`
- `media/`
- `staticfiles/`
- `firebase-service-account.json`

## 4. Структура репозитория

```
dofamine-server/
├── accounts/                 # Django приложение
├── core/                    # Настройки Django
├── media/                   # Медиа файлы (в .gitignore)
├── staticfiles/             # Статические файлы (в .gitignore)
├── requirements.txt         # Python зависимости
├── docker-compose.yml       # Docker конфигурация
├── Dockerfile              # Docker образ
├── nginx.conf              # Nginx конфигурация
├── production.env          # Продакшн настройки
├── deploy_from_github.sh   # Скрипт деплоя
├── .gitignore              # Git ignore файл
└── README.md               # Документация
```

## 5. Обновление кода

После изменений:

```bash
# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Загрузить на GitHub
git push origin main
```

## 6. Деплой с GitHub

После загрузки на GitHub:

```bash
# На сервере
chmod +x deploy_from_github.sh
./deploy_from_github.sh YOUR_USERNAME/dofamine-server main YOUR_SERVER_IP your-domain.com
```

## 7. Автоматический деплой (опционально)

Можно настроить GitHub Actions для автоматического деплоя:

1. Создайте `.github/workflows/deploy.yml`
2. Настройте секреты в GitHub
3. При каждом пуше в `main` будет автоматический деплой

## 🔐 Безопасность

### Секреты, которые НЕ должны попасть в Git:
- `SECRET_KEY`
- `DB_PASSWORD`
- `OPENAI_API_KEY`
- `TWILIO_AUTH_TOKEN`
- `firebase-service-account.json`

### Используйте переменные окружения:
```bash
# На сервере создайте .env файл
nano /opt/dofamine/.env
```

## 📋 Чек-лист перед загрузкой

- [ ] Удален `firebase-service-account.json`
- [ ] Создан `.gitignore`
- [ ] Обновлен `README.md`
- [ ] Настроен `production.env`
- [ ] Создан `deploy_from_github.sh`
- [ ] Проверены все файлы на наличие секретов
