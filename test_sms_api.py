#!/usr/bin/env python3
"""
Тестовый скрипт для проверки SMS API
"""
import requests
import json
import sys

def test_sms_api(base_url):
    """Тестирует SMS API endpoints"""
    
    # Тест отправки SMS
    print("🔍 Тестируем отправку SMS...")
    send_data = {
        'phone_number': '79999999999'  # Тестовый номер
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/sms/send/",
            json=send_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SMS отправлен успешно")
            if 'debug_code' in data:
                print(f"Debug код: {data['debug_code']}")
                return data['debug_code']
        else:
            print(f"❌ Ошибка отправки SMS: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Исключение при отправке SMS: {e}")
        return None

def test_sms_verify(base_url, phone_number, code):
    """Тестирует верификацию SMS кода"""
    
    print(f"\n🔍 Тестируем верификацию SMS кода {code} для {phone_number}...")
    
    verify_data = {
        'phone_number': phone_number,
        'code': code
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/sms/verify/",
            json=verify_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ SMS код верифицирован успешно")
            return True
        else:
            print(f"❌ Ошибка верификации SMS: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при верификации SMS: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Использование: python test_sms_api.py <BASE_URL>")
        print("Пример: python test_sms_api.py http://localhost:8000")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🚀 Тестируем SMS API на {base_url}")
    print("=" * 50)
    
    # Тест отправки SMS
    debug_code = test_sms_api(base_url)
    
    if debug_code:
        # Тест верификации SMS
        test_sms_verify(base_url, '79999999999', debug_code)
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено")

if __name__ == "__main__":
    main()
