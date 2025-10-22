#!/usr/bin/env python3
import requests
import json

# Тестируем SMS verify endpoint
url = "http://localhost:8000/api/auth/sms/verify/"
data = {
    "phone_number": "+77765114014",
    "code": "123456"
}

print("🔍 Тестируем SMS verify endpoint...")
print(f"📞 Номер: {data['phone_number']}")
print(f"🔑 Код: {data['code']}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\n🌐 HTTP Status: {response.status_code}")
    
    try:
        result = response.json()
        print(f"📋 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except:
        print(f"📋 Response (text): {response.text}")
    
    if response.status_code == 503:
        print("\n✅ УСПЕХ: Заглушка 'в разработке' работает!")
    else:
        print(f"\n❌ ОШИБКА: Ожидался статус 503, получен {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

