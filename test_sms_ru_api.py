#!/usr/bin/env python3
"""
Тестовый скрипт для проверки SMS.RU API
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.sms_ru_service import SMSRuService


def test_sms_ru_service():
    """Тестирует сервис SMS.RU"""
    print("🧪 Тестирование SMS.RU Service...")
    print("=" * 50)
    
    # Создаем экземпляр сервиса
    service = SMSRuService()
    
    # Тестируем нормализацию номера
    print("📱 Тестирование нормализации номеров:")
    test_numbers = [
        "87088043414",
        "+77088043414", 
        "77088043414",
        "7088043414",
        "8 708 804 34 14"
    ]
    
    for number in test_numbers:
        normalized = service.normalize_phone_number(number)
        print(f"  {number} -> {normalized}")
    
    print("\n🔑 Проверка учетных данных:")
    if service.login and service.password:
        print(f"  ✅ Логин/пароль настроены: {service.login[:3]}...")
    elif service.api_key:
        print(f"  ✅ API ключ настроен: {service.api_key[:3]}...")
    else:
        print("  ⚠️  Учетные данные не настроены, будет использоваться debug режим")
    
    print("\n📤 Тестирование отправки SMS:")
    test_phone = "+77088043414"  # Замените на свой номер для тестирования
    test_message = "Тестовое сообщение от Dopamine Control"
    
    try:
        # Тестируем отправку SMS
        result = service.send_sms(test_phone, test_message)
        print(f"  ✅ SMS отправлена успешно")
        print(f"  📋 Результат: {result}")
    except Exception as e:
        print(f"  ❌ Ошибка отправки SMS: {e}")
    
    print("\n🔐 Тестирование кода подтверждения:")
    try:
        # Тестируем отправку кода подтверждения
        result = service.send_verification_code(test_phone)
        print(f"  ✅ Код подтверждения отправлен")
        print(f"  📋 Результат: {result}")
        
        if result.get('code'):
            print(f"  🔢 Код для тестирования: {result['code']}")
            
            # Тестируем проверку кода
            verification_result = service.verify_code(test_phone, result['code'])
            print(f"  ✅ Проверка кода: {'Успешно' if verification_result else 'Неудачно'}")
            
    except Exception as e:
        print(f"  ❌ Ошибка работы с кодом подтверждения: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено!")


if __name__ == "__main__":
    test_sms_ru_service()


