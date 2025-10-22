# 🔧 Руководство по диагностике SMS аутентификации

## 🚨 Проблема: Ошибка 500 при верификации SMS кода

### ✅ Что было исправлено:

1. **Добавлено логирование Django** - теперь все ошибки будут записываться в `django.log`
2. **Улучшена обработка ошибок** в `SmsVerifyCodeView` с подробным логированием
3. **Улучшено логирование Twilio сервиса** для отслеживания ошибок API

### 🔍 Диагностика проблемы:

#### 1. Проверьте логи сервера:
```bash
# На сервере выполните:
cd /path/to/your/server
tail -f django.log

# Или если используете Docker:
docker-compose logs -f web
```

#### 2. Проверьте переменные окружения Twilio:
```bash
# Убедитесь что эти переменные установлены:
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN  
echo $TWILIO_VERIFY_SERVICE_SID
```

#### 3. Тестирование API:
```bash
# Запустите тестовый скрипт:
cd server
python test_sms_api.py http://your-server-url
```

### 🐛 Возможные причины ошибки 500:

#### 1. **Отсутствуют переменные окружения Twilio**
- Проверьте `.env` файл на сервере
- Убедитесь что `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE_SID` установлены

#### 2. **Проблемы с базой данных**
- Проверьте подключение к PostgreSQL
- Убедитесь что миграции выполнены: `python manage.py migrate`

#### 3. **Проблемы с кешем Redis**
- Проверьте доступность Redis (если используется)
- В debug режиме используется Django cache (может быть проблемой)

#### 4. **Проблемы с JWT токенами**
- Проверьте `SECRET_KEY` в настройках
- Убедитесь что `djangorestframework-simplejwt` установлен

### 🔧 Шаги по исправлению:

#### 1. Обновите код на сервере:
```bash
# На сервере:
git pull origin main
# Перезапустите сервисы:
docker-compose down
docker-compose up -d --build
```

#### 2. Проверьте логи после обновления:
```bash
docker-compose logs -f web | grep -i "sms\|error\|exception"
```

#### 3. Если проблема остается, проверьте Twilio:
```python
# Создайте файл test_twilio.py на сервере:
import os
from twilio.rest import Client

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
verify_service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')

print(f"Account SID: {account_sid}")
print(f"Auth Token: {auth_token[:10]}..." if auth_token else "None")
print(f"Verify Service SID: {verify_service_sid}")

if all([account_sid, auth_token, verify_service_sid]):
    try:
        client = Client(account_sid, auth_token)
        print("✅ Twilio client создан успешно")
    except Exception as e:
        print(f"❌ Ошибка создания Twilio client: {e}")
else:
    print("❌ Не все переменные Twilio установлены")
```

### 📱 Проверка Flutter приложения:

#### 1. Проверьте URL API в приложении:
```dart
// В flutter_app/lib/config/app_config.dart
// Убедитесь что BASE_URL указывает на правильный сервер
```

#### 2. Проверьте обработку ошибок в Flutter:
```dart
// В flutter_app/lib/services/phone_auth_service.dart
// Добавьте больше логирования в verifySmsCode
```

### 🚀 Временное решение (Debug режим):

Если Twilio не работает, приложение автоматически переключится в debug режим:
- SMS коды будут генерироваться локально
- Коды будут возвращаться в ответе API (только в DEBUG режиме)
- Коды сохраняются в кеше на 10 минут

### 📞 Контакты для поддержки:

Если проблема не решается:
1. Соберите логи: `docker-compose logs web > logs.txt`
2. Проверьте переменные окружения
3. Запустите тестовый скрипт и пришлите результаты

### 🔄 Мониторинг:

После исправления отслеживайте:
- Логи Django: `tail -f django.log`
- Статистику SMS: Twilio Console
- Ошибки приложения: Flutter console

