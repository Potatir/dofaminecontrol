import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Сервис для работы с Firebase Authentication"""
    
    def __init__(self):
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Инициализация Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                # Для продакшена используем переменную окружения с JSON ключом
                firebase_credentials = getattr(settings, 'FIREBASE_CREDENTIALS', None)
                
                if firebase_credentials:
                    # Если есть путь к файлу с ключами
                    if isinstance(firebase_credentials, str):
                        cred = credentials.Certificate(firebase_credentials)
                    else:
                        # Если это словарь с данными ключа
                        cred = credentials.Certificate(firebase_credentials)
                else:
                    # Используем дефолтные credentials (для Google Cloud)
                    cred = credentials.ApplicationDefault()
                
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK инициализирован успешно")
            except Exception as e:
                logger.error(f"Ошибка инициализации Firebase: {e}")
                raise
    
    def verify_id_token(self, id_token):
        """
        Проверяет Firebase ID Token и возвращает данные пользователя
        
        Args:
            id_token (str): Firebase ID Token
            
        Returns:
            dict: Данные пользователя из Firebase
            
        Raises:
            firebase_auth.InvalidIdTokenError: Если токен недействителен
            firebase_auth.ExpiredIdTokenError: Если токен истек
        """
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            logger.info(f"Firebase токен проверен для пользователя: {decoded_token.get('uid')}")
            return decoded_token
        except firebase_auth.InvalidIdTokenError as e:
            logger.error(f"Недействительный Firebase токен: {e}")
            raise
        except firebase_auth.ExpiredIdTokenError as e:
            logger.error(f"Истекший Firebase токен: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка проверки Firebase токена: {e}")
            raise
    
    def get_user_by_uid(self, uid):
        """
        Получает данные пользователя из Firebase по UID
        
        Args:
            uid (str): Firebase UID пользователя
            
        Returns:
            firebase_auth.UserRecord: Данные пользователя
        """
        try:
            user_record = firebase_auth.get_user(uid)
            return user_record
        except firebase_auth.UserNotFoundError as e:
            logger.error(f"Пользователь не найден в Firebase: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка получения пользователя из Firebase: {e}")
            raise
    
    def create_user(self, phone_number, display_name=None):
        """
        Создает пользователя в Firebase
        
        Args:
            phone_number (str): Номер телефона
            display_name (str, optional): Отображаемое имя
            
        Returns:
            firebase_auth.UserRecord: Созданный пользователь
        """
        try:
            user_record = firebase_auth.create_user(
                phone_number=phone_number,
                display_name=display_name
            )
            logger.info(f"Пользователь создан в Firebase: {user_record.uid}")
            return user_record
        except Exception as e:
            logger.error(f"Ошибка создания пользователя в Firebase: {e}")
            raise
    
    def update_user_phone(self, uid, phone_number):
        """
        Обновляет номер телефона пользователя в Firebase
        
        Args:
            uid (str): Firebase UID пользователя
            phone_number (str): Новый номер телефона
        """
        try:
            firebase_auth.update_user(uid, phone_number=phone_number)
            logger.info(f"Номер телефона обновлен для пользователя: {uid}")
        except Exception as e:
            logger.error(f"Ошибка обновления номера телефона: {e}")
            raise
    
    def delete_user(self, uid):
        """
        Удаляет пользователя из Firebase
        
        Args:
            uid (str): Firebase UID пользователя
        """
        try:
            firebase_auth.delete_user(uid)
            logger.info(f"Пользователь удален из Firebase: {uid}")
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя из Firebase: {e}")
            raise
    
    def verify_phone_number_token(self, id_token):
        """
        Проверяет, что токен содержит верифицированный номер телефона
        
        Args:
            id_token (str): Firebase ID Token
            
        Returns:
            dict: Данные пользователя с проверкой номера телефона
        """
        decoded_token = self.verify_id_token(id_token)
        
        # Проверяем, что номер телефона верифицирован
        phone_number = decoded_token.get('phone_number')
        if not phone_number:
            raise ValueError("Номер телефона не найден в токене")
        
        firebase_verified = decoded_token.get('firebase', {}).get('identities', {}).get('phone', [])
        if not firebase_verified:
            raise ValueError("Номер телефона не верифицирован в Firebase")
        
        return {
            'uid': decoded_token.get('uid'),
            'phone_number': phone_number,
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
            'picture': decoded_token.get('picture'),
            'email_verified': decoded_token.get('email_verified', False),
            'phone_verified': True,
        }












