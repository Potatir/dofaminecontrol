import os
import random
from twilio.rest import Client
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TwilioSMSService:
    """Сервис для отправки SMS через Twilio Verify API"""
    
    def __init__(self):
        # Получаем credentials из переменных окружения
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.verify_service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')
        
        if not all([self.account_sid, self.auth_token, self.verify_service_sid]):
            logger.warning("Twilio credentials not configured. Using debug mode.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info(f"Twilio client initialized with Account SID: {self.account_sid[:10]}...")
    
    def generate_verification_code(self):
        """Генерирует 6-значный код подтверждения"""
        return str(random.randint(100000, 999999))
    
    def normalize_phone_number(self, phone_number):
        """
        Нормализует номер телефона в международный формат для Twilio
        
        Args:
            phone_number (str): Номер в любом формате
            
        Returns:
            str: Номер в формате +7XXXXXXXXXX
        """
        # Убираем все нецифровые символы кроме +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Если номер начинается с 8, заменяем на +7
        if cleaned.startswith('8') and len(cleaned) == 11:
            cleaned = '+7' + cleaned[1:]
        
        # Если номер начинается с 7, добавляем +
        elif cleaned.startswith('7') and len(cleaned) == 11:
            cleaned = '+' + cleaned
            
        # Если номер не начинается с +, добавляем +7 для Казахстана/России
        elif not cleaned.startswith('+'):
            if len(cleaned) == 10:
                cleaned = '+7' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('7'):
                cleaned = '+' + cleaned
            else:
                # Для других случаев добавляем +7
                cleaned = '+7' + cleaned[-10:] if len(cleaned) >= 10 else '+7' + cleaned
        
        return cleaned
    
    def send_verification_code(self, phone_number):
        """
        Отправляет SMS с кодом подтверждения через Twilio Verify API
        
        Args:
            phone_number (str): Номер телефона в любом формате
            
        Returns:
            dict: {'success': bool, 'code': str, 'message': str}
        """
        try:
            # Нормализуем номер телефона
            normalized_phone = self.normalize_phone_number(phone_number)
            logger.info(f"Отправка SMS на {phone_number} -> {normalized_phone}")
            
            # Если Twilio не настроен, используем debug режим
            if not self.client:
                code = self.generate_verification_code()
                cache_key = f'sms_code_{normalized_phone}'
                cache.set(cache_key, code, timeout=600)  # 10 минут
                logger.warning(f"Twilio not configured. Debug code for {normalized_phone}: {code}")
                return {
                    'success': True,
                    'code': code,
                    'message': f'Код для отладки: {code} (Twilio не настроен)'
                }
            
            # Отправляем верификацию через Twilio Verify API
            logger.info(f"Отправка verification через Twilio API для {normalized_phone}")
            logger.info(f"Service SID: {self.verify_service_sid}")
            
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=normalized_phone, channel='sms')
            
            logger.info(f"Verification отправлена на {normalized_phone}. Status: {verification.status}")
            
            return {
                'success': True,
                'message': 'SMS код отправлен успешно',
                'sid': verification.sid,
                'status': verification.status
            }
            
        except Exception as e:
            logger.error(f"Ошибка отправки verification на {phone_number}: {e}")
            # В случае ошибки используем fallback на debug режим
            normalized_phone = self.normalize_phone_number(phone_number)
            code = self.generate_verification_code()
            cache_key = f'sms_code_{normalized_phone}'
            cache.set(cache_key, code, timeout=600)
            return {
                'success': True,
                'code': code,
                'message': f'Ошибка Twilio, используется debug код: {code}'
            }
    
    def verify_code(self, phone_number, code):
        """
        Проверяет код подтверждения через Twilio Verify API
        
        Args:
            phone_number (str): Номер телефона
            code (str): Код для проверки
            
        Returns:
            bool: True если код верный, False иначе
        """
        try:
            # Нормализуем номер телефона
            normalized_phone = self.normalize_phone_number(phone_number)
            
            # Если Twilio не настроен, проверяем через кеш (debug режим)
            if not self.client:
                cache_key = f'sms_code_{normalized_phone}'
                saved_code = cache.get(cache_key)
                
                if not saved_code:
                    logger.warning(f"Код не найден для {normalized_phone} (истек или не был отправлен)")
                    return False
                
                if str(saved_code) == str(code):
                    cache.delete(cache_key)
                    logger.info(f"Debug код успешно проверен для {normalized_phone}")
                    return True
                
                logger.warning(f"Неверный debug код для {normalized_phone}")
                return False
            
            # Проверяем код через Twilio Verify API
            verification_check = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=normalized_phone, code=code)
            
            logger.info(f"Verification check для {normalized_phone}. Status: {verification_check.status}")
            
            # Twilio возвращает "approved" если код верный
            return verification_check.status == 'approved'
            
        except Exception as e:
            logger.error(f"Ошибка проверки кода для {phone_number}: {e}")
            return False
    
    def clear_code(self, phone_number):
        """Удаляет код подтверждения из кеша"""
        normalized_phone = self.normalize_phone_number(phone_number)
        cache_key = f'sms_code_{normalized_phone}'
        cache.delete(cache_key)
        logger.info(f"Код удален для {normalized_phone}")

