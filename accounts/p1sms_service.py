import os
import random
import requests
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class P1SMSService:
    """Сервис для отправки SMS через P1SMS API"""

    def __init__(self):
        self.api_key = settings.P1SMS_API_KEY

        if not self.api_key:
            logger.warning("P1SMS API key not configured. Using debug mode.")
        else:
            logger.info(f"P1SMS client initialized with API key: {self.api_key[:10]}...")

    def generate_verification_code(self):
        """Генерирует 6-значный код подтверждения"""
        return str(random.randint(100000, 999999))

    def normalize_phone_number(self, phone_number):
        """
        Нормализует номер телефона в формат 7XXXXXXXXXX для P1SMS
        """
        cleaned = ''.join(c for c in phone_number if c.isdigit())

        if cleaned.startswith('8') and len(cleaned) == 11:
            cleaned = '7' + cleaned[1:]
        elif cleaned.startswith('+7') and len(cleaned) == 12:
            cleaned = cleaned[1:]
        elif cleaned.startswith('7') and len(cleaned) == 11:
            pass # Уже в нужном формате
        elif len(cleaned) == 10: # Предполагаем, что это 10-значный номер без 7 или 8
            cleaned = '7' + cleaned
        
        return cleaned

    def send_sms(self, phone: str, text: str, channel: str = "digit", sender: str = None):
        """
        Отправляет SMS через P1SMS API согласно документации.
        """
        try:
            normalized_phone = self.normalize_phone_number(phone)
            logger.info(f"Отправка SMS через P1SMS на {normalized_phone}")

            if not self.api_key:
                raise Exception("P1SMS API key not configured.")

            # Формируем данные согласно документации
            data = {
                "apiKey": self.api_key,
                "sms": [
                    {
                        "channel": channel,
                        "phone": normalized_phone,
                        "text": text
                    }
                ]
            }

            # Добавляем отправителя если нужен (для char, viber, whatsapp каналов)
            if sender and channel in ["char", "viber", "whatsapp"]:
                data["sms"][0]["sender"] = sender

            url = "https://admin.p1sms.ru/apiSms/create"
            headers = {
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }

            logger.info(f"URL: {url}")
            logger.info(f"Data: {data}")

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            p1sms_result = response.json()
            logger.info(f"P1SMS response: {p1sms_result}")

            if p1sms_result.get('status') == 'success':
                # Проверяем статус каждого сообщения
                for sms_data in p1sms_result.get('data', []):
                    if sms_data.get('status') == 'sent':
                        logger.info(f"SMS успешно отправлена на {normalized_phone}")
                        return {'success': True, 'p1sms_result': p1sms_result}
                    else:
                        error_desc = sms_data.get('errorDescription', 'Unknown error')
                        error_code = sms_data.get('errorCode', 'N/A')
                        logger.error(f"P1SMS API вернул ошибку для {normalized_phone}: {error_desc} (Code: {error_code})")
                        return {'success': False, 'message': f'P1SMS API error: {error_desc}', 'p1sms_result': p1sms_result}
                
                # Если дошли сюда, значит нет сообщений со статусом 'sent'
                logger.error(f"P1SMS API не вернул статус 'sent' для {normalized_phone}")
                return {'success': False, 'message': 'P1SMS API did not return sent status', 'p1sms_result': p1sms_result}
            else:
                error_desc = p1sms_result.get('errorDescription', 'Unknown error')
                error_code = p1sms_result.get('errorCode', 'N/A')
                logger.error(f"P1SMS API вернул ошибку: {error_desc} (Code: {error_code})")
                return {'success': False, 'message': f'P1SMS API error: {error_desc}', 'p1sms_result': p1sms_result}

        except requests.exceptions.RequestException as e:
            logger.error(f"P1SMS HTTP error: {e}")
            return {'success': False, 'message': f'P1SMS HTTP error: {e}'}
        except Exception as e:
            logger.error(f"Ошибка отправки SMS через P1SMS на {phone}: {e}")
            return {'success': False, 'message': f'Ошибка отправки SMS: {e}'}

    def send_verification_code(self, phone_number):
        """
        Отправляет SMS с кодом подтверждения через P1SMS API.
        """
        normalized_phone = self.normalize_phone_number(phone_number)
        code = self.generate_verification_code()
        cache_key = f'sms_code_{normalized_phone}'
        cache.set(cache_key, code, timeout=600)  # 10 минут

        if not self.api_key:
            logger.error(f"P1SMS API key not configured!")
            return {
                'success': False,
                'message': 'P1SMS API key not configured'
            }
        
        text = f"Ваш код подтверждения: {code}"
        result = self.send_sms(phone_number, text, channel="telegram_auth")

        if result['success']:
            logger.info(f"SMS отправлена на {normalized_phone} через P1SMS")
            return {
                'success': True,
                'message': 'SMS код отправлен успешно',
                'code': code,
                'p1sms_result': result.get('p1sms_result')
            }
        else:
            logger.error(f"Ошибка отправки SMS на {phone_number}: {result['message']}")
            return {
                'success': False,
                'message': f'Ошибка отправки SMS: {result["message"]}'
            }

    def verify_code(self, phone_number, code):
        """
        Проверяет код подтверждения через кеш (для P1SMS нет прямого API для проверки).
        """
        normalized_phone = self.normalize_phone_number(phone_number)
        cache_key = f'sms_code_{normalized_phone}'
        saved_code = cache.get(cache_key)

        if not saved_code:
            logger.warning(f"Код не найден для {normalized_phone} (истек или не был отправлен)")
            return False

        if str(saved_code) == str(code):
            cache.delete(cache_key)
            logger.info(f"Код успешно проверен для {normalized_phone}")
            return True
        else:
            logger.warning(f"Неверный код для {normalized_phone}")
            return False

    def clear_code(self, phone_number):
        """Удаляет код подтверждения из кеша"""
        normalized_phone = self.normalize_phone_number(phone_number)
        cache_key = f'sms_code_{normalized_phone}'
        cache.delete(cache_key)
        logger.info(f"Код удален для {normalized_phone}")
