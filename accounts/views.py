from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .models import User, Habit, DailyNote, AppUsage, ChatSession, ChatMessage, ChatAttachment, DailyTimeline, App, AppUsageRecord, UserTestResult, Achievement, AchievementStats
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, HabitSerializer, 
    DailyNoteSerializer, AppUsageSerializer, ChatSessionSerializer, 
    ChatMessageSerializer, SendMessageSerializer, ChatAttachmentSerializer,
    DailyTimelineSerializer, AppSerializer, AppCategoryUpdateSerializer,
    UserTestResultSerializer, AchievementSerializer, AchievementSyncSerializer,
    AchievementStatsSerializer
)
from .services import ChatGPTService, FileUploadService
from .p1sms_service import P1SMSService

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user for token generation
        username = request.data.get('username')
        password = request.data.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if not user:
            # Try with email
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            # Try with phone
            try:
                user_obj = User.objects.get(phone_number=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            return Response({'error': 'Unable to log in with provided credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# SMS Login stubs
@api_view(['POST'])
def sms_request_view(request):
    # TODO: Implement SMS sending
    return Response({'message': 'SMS code sent'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def sms_verify_view(request):
    # TODO: Implement SMS verification
    return Response({'message': 'SMS verified'}, status=status.HTTP_200_OK)


# Social Login stubs
@api_view(['POST'])
def social_login_view(request):
    provider = request.data.get('provider')
    # TODO: Implement social login
    return Response({'message': f'{provider} login not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)


# Habit Views
class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        habit_type = self.request.query_params.get('type', None)
        queryset = Habit.objects.filter(user=self.request.user)
        if habit_type:
            queryset = queryset.filter(habit_type=habit_type)
        return queryset


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitResetView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            habit = Habit.objects.get(pk=pk, user=request.user)
            # Сбрасываем дату начала на текущий момент
            habit.start_date = timezone.now()
            habit.save()
            return Response({'message': 'Progress reset successfully'})
        except Habit.DoesNotExist:
            return Response({'error': 'Habit not found'}, status=404)


# Alias for existing views
RegisterView = UserRegistrationView
MeView = ManageUserView
FlexibleTokenObtainPairView = CustomTokenObtainPairView

# SMS stubs
class SmsRequestCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ВРЕМЕННО: Закомментировано для тестирования
        # # Отправляем SMS через P1SMS
        # p1sms_service = P1SMSService()
        # result = p1sms_service.send_verification_code(phone_number)
        # 
        # if result['success']:
        #     return Response({
        #         'message': result['message'],
        #         'phone_number': phone_number,
        #         # В debug режиме возвращаем код для тестирования
        #         'debug_code': result.get('code') if settings.DEBUG else None
        #     }, status=status.HTTP_200_OK)
        # else:
        #     return Response({
        #         'error': result['message']
        #     }, status=status.HTTP_400_BAD_REQUEST)
        
        # ВРЕМЕННО: Возвращаем успех без отправки SMS
        return Response({
            'message': 'SMS код отправлен успешно (в разработке)',
            'phone_number': phone_number,
            'debug_code': '123456'  # Фиксированный код для тестирования
        }, status=status.HTTP_200_OK)

class SmsVerifyCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            phone_number = request.data.get('phone_number')
            firebase_id_token = request.data.get('firebase_id_token')
            
            logger.info(f"Firebase verification attempt for phone: {phone_number}")

            if not phone_number:
                logger.warning(f"Missing phone_number: phone={phone_number}")
                return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not firebase_id_token:
                logger.warning(f"Missing firebase_id_token for phone: {phone_number}")
                return Response({'error': 'Firebase ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверяем Firebase ID token
            try:
                from .firebase_auth_service import FirebaseAuthService
                firebase_service = FirebaseAuthService()
                decoded_token = firebase_service.verify_id_token(firebase_id_token)
                
                logger.info(f"Firebase token verified successfully for phone: {phone_number}")
                
                # Получаем номер телефона из Firebase token
                firebase_phone = decoded_token.get('phone_number')
                if not firebase_phone:
                    logger.warning(f"Phone number not found in Firebase token for phone: {phone_number}")
                    return Response({'error': 'Phone number not found in Firebase token'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Нормализуем номер из Firebase (формат +7XXXXXXXXXX)
                firebase_phone_clean = firebase_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                # Нормализуем номер из запроса
                phone_number_clean = phone_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                # Если номер из запроса начинается с 8, заменяем на 7
                if phone_number_clean.startswith('8') and len(phone_number_clean) == 11:
                    phone_number_clean = '7' + phone_number_clean[1:]
                
                # Если номер из запроса имеет 10 цифр, добавляем 7
                if len(phone_number_clean) == 10:
                    phone_number_clean = '7' + phone_number_clean
                
                # Проверяем что номера совпадают
                if firebase_phone_clean != phone_number_clean:
                    logger.warning(f"Phone number mismatch: Firebase={firebase_phone_clean}, Request={phone_number_clean}")
                    return Response({'error': 'Phone number mismatch'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Используем номер из Firebase для дальнейшей работы
                phone_number = firebase_phone_clean
            except Exception as e:
                logger.error(f"Firebase verification error for {phone_number}: {str(e)}")
                return Response({'error': f'Firebase verification failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Using normalized phone number: {phone_number}")

            # Логика входа/регистрации
            try:
                user = User.objects.get(phone_number=phone_number)
                is_new = False
                logger.info(f"Existing user found: {user.username}")
            except User.DoesNotExist:
                username = f"user_{phone_number}"
                # На случай коллизии username
                base_username = username
                suffix = 1
                while User.objects.filter(username=username).exists():
                    suffix += 1
                    username = f"{base_username}_{suffix}"
                user = User.objects.create_user(
                    username=username,
                    phone_number=phone_number,
                    password='dummy_password_for_sms_user',  # безопасная заглушка
                )
                is_new = True
                logger.info(f"New user created: {username}")
            except Exception as e:
                logger.error(f"Database error during user lookup/creation: {str(e)}")
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                logger.info(f"Tokens generated successfully for user: {user.username}")

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'phone_number': user.phone_number,
                        'email': user.email,
                    },
                    'isNewUser': is_new
                }, status=status.HTTP_201_CREATED if is_new else status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Token generation error for user {user.username}: {str(e)}")
                return Response({'error': f'Token generation error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # ЗАКОММЕНТИРОВАНО: Логика входа/регистрации временно отключена
            # # Нормализуем номер (уберем пробелы)
            # phone_number = phone_number.strip()
            # logger.info(f"Normalized phone number: {phone_number}")

            # # Логика входа/регистрации
            # try:
            #     user = User.objects.get(phone_number=phone_number)
            #     is_new = False
            #     logger.info(f"Existing user found: {user.username}")
            # except User.DoesNotExist:
            #     username = f"user_{phone_number}"
            #     # На случай коллизии username
            #     base_username = username
            #     suffix = 1
            #     while User.objects.filter(username=username).exists():
            #         suffix += 1
            #         username = f"{base_username}_{suffix}"
            #     user = User.objects.create_user(
            #         username=username,
            #         phone_number=phone_number,
            #         password='dummy_password_for_sms_user',  # безопасная заглушка
            #     )
            #     is_new = True
            #     logger.info(f"New user created: {username}")
            # except Exception as e:
            #     logger.error(f"Database error during user lookup/creation: {str(e)}")
            #     return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # try:
            #     from rest_framework_simplejwt.tokens import RefreshToken
            #     refresh = RefreshToken.for_user(user)
            #     
            #     logger.info(f"Tokens generated successfully for user: {user.username}")

            #     return Response({
            #         'access': str(refresh.access_token),
            #         'refresh': str(refresh),
            #         'user': {
            #             'id': user.id,
            #             'username': user.username,
            #             'phone_number': user.phone_number,
            #             'email': user.email,
            #         },
            #         'isNewUser': is_new
            #     }, status=status.HTTP_201_CREATED if is_new else status.HTTP_200_OK)
            # except Exception as e:
            #     logger.error(f"Token generation error for user {user.username}: {str(e)}")
            #     return Response({'error': f'Token generation error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in SMS verification: {str(e)}")
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            email = request.data.get('email')
            firebase_id_token = request.data.get('firebase_id_token')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            
            logger.info(f"Firebase email verification attempt for email: {email}")

            if not email:
                logger.warning(f"Missing email")
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not firebase_id_token:
                logger.warning(f"Missing firebase_id_token for email: {email}")
                return Response({'error': 'Firebase ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверяем Firebase ID token
            try:
                from .firebase_auth_service import FirebaseAuthService
                firebase_service = FirebaseAuthService()
                decoded_token = firebase_service.verify_id_token(firebase_id_token)
                
                logger.info(f"Firebase token verified successfully for email: {email}")
                
                # Получаем email из Firebase token
                firebase_email = decoded_token.get('email')
                if not firebase_email:
                    logger.warning(f"Email not found in Firebase token")
                    return Response({'error': 'Email not found in Firebase token'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Проверяем что email совпадает (case-insensitive)
                if firebase_email.lower() != email.lower():
                    logger.warning(f"Email mismatch: Firebase={firebase_email}, Request={email}")
                    return Response({'error': 'Email mismatch'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Используем email из Firebase для дальнейшей работы
                email = firebase_email.lower()
            except Exception as e:
                logger.error(f"Firebase verification error for {email}: {str(e)}")
                return Response({'error': f'Firebase verification failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Using email: {email}")

            # Логика входа/регистрации
            try:
                user = User.objects.filter(email__iexact=email).first()
                is_new = False
                if user:
                    logger.info(f"Existing user found: {user.username}")
                    # Обновляем имя и фамилию если они переданы
                    if first_name:
                        user.first_name = first_name
                    if last_name:
                        user.last_name = last_name
                    if first_name or last_name:
                        user.save()
                else:
                    # Создаем нового пользователя
                    username = f"user_{email.split('@')[0]}"
                    base_username = username
                    suffix = 1
                    while User.objects.filter(username=username).exists():
                        suffix += 1
                        username = f"{base_username}_{suffix}"
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='dummy_password_for_email_user',  # безопасная заглушка
                        first_name=first_name or '',
                        last_name=last_name or '',
                    )
                    is_new = True
                    logger.info(f"New user created: {username}")
            except Exception as e:
                logger.error(f"Database error during user lookup/creation: {str(e)}")
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                logger.info(f"Tokens generated successfully for user: {user.username}")

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'phone_number': user.phone_number,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'isNewUser': is_new
                }, status=status.HTTP_201_CREATED if is_new else status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Token generation error for user {user.username}: {str(e)}")
                return Response({'error': f'Token generation error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in email verification: {str(e)}")
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete account view
class DeleteAccountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """Удалить аккаунт пользователя"""
        try:
            user = request.user
            print(f"DEBUG: Deleting account for user {user.username} (phone: {user.phone_number})")
            
            # Удаляем пользователя
            user.delete()
            
            return Response({
                'message': 'Account deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"DEBUG: Error deleting account: {e}")
            return Response({
                'error': 'Failed to delete account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Test results view
class TestResultView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTestResultSerializer
    
    def post(self, request):
        """Сохранить результаты теста пользователя"""
        try:
            # Получаем или создаем результат теста для пользователя
            test_result, created = UserTestResult.objects.get_or_create(
                user=request.user,
                defaults={}
            )
            
            # Обновляем поля теста
            for field in ['question_1', 'question_2', 'question_3', 'question_4', 'question_5']:
                if field in request.data:
                    setattr(test_result, field, request.data[field])
            
            test_result.save()
            
            serializer = UserTestResultSerializer(test_result)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            print(f"DEBUG: Error saving test result: {e}")
            return Response({
                'error': 'Failed to save test result'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Получить результаты теста пользователя"""
        try:
            test_result = UserTestResult.objects.filter(user=request.user).first()
            if test_result:
                serializer = UserTestResultSerializer(test_result)
                return Response(serializer.data)
            else:
                return Response({'message': 'No test results found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Failed to get test results'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Social login stub
class SocialLoginStubView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, provider=None):
        # Для Google авторизации
        if request.path.endswith('/auth/google/'):
            return self._handle_google_login(request)
        
        # Для других провайдеров
        if provider:
            return Response({'message': f'{provider} login not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)
        
        return Response({'error': 'Provider not specified'}, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_google_login(self, request):
        access_token = request.data.get('access_token')
        id_token = request.data.get('id_token')
        email = request.data.get('email')
        name = request.data.get('name')
        
        if not access_token or not id_token:
            return Response({'error': 'Google tokens are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Валидация Google токенов
        # Пока что заглушка - создаем/находим пользователя по email
        
        try:
            # Ищем существующего пользователя по email
            user = User.objects.get(email=email)
            
            # Обновляем данные пользователя
            if name:
                user.first_name = name.split()[0] if name else ''
                user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
            user.save()
            
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Создаем нового пользователя
            username = f"google_{email.split('@')[0]}"  # Генерируем username из email
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                password='',  # Без пароля для Google входа
            )
            
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)


class FirebasePhoneLoginView(generics.GenericAPIView):
    """Аутентификация через Firebase Phone Auth"""
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        firebase_id_token = request.data.get('firebase_id_token')
        
        if not phone_number or not firebase_id_token:
            return Response({
                'error': 'phone_number and firebase_id_token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Инициализируем Firebase сервис
            firebase_service = FirebaseAuthService()
            
            # Проверяем Firebase токен
            firebase_user_data = firebase_service.verify_phone_number_token(firebase_id_token)
            
            # Проверяем, что номер телефона в токене совпадает с переданным
            if firebase_user_data['phone_number'] != phone_number:
                return Response({
                    'error': 'Phone number mismatch'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаем или находим пользователя
            firebase_uid = firebase_user_data['uid']
            username = f"firebase_{firebase_uid}"
            
            try:
                user = User.objects.get(username=username)
                # Обновляем номер телефона если изменился
                if user.phone_number != phone_number:
                    user.phone_number = phone_number
                    user.save()
            except User.DoesNotExist:
                # Создаем нового пользователя
                user = User.objects.create_user(
                    username=username,
                    phone_number=phone_number,
                    email=firebase_user_data.get('email', ''),
                    first_name=firebase_user_data.get('name', '').split(' ')[0] if firebase_user_data.get('name') else '',
                    last_name=' '.join(firebase_user_data.get('name', '').split(' ')[1:]) if firebase_user_data.get('name') else '',
                )
            
            # Генерируем JWT токены
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone_number': user.phone_number,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_new_user': False,  # Всегда False для Firebase, так как пользователь уже верифицирован
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Firebase authentication failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# Daily Notes Views
class DailyNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyNote.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        daily_note = serializer.save()
        
        # Добавляем примеры использования приложений (заглушка)
        app_usage_data = [
            {'app_name': 'Telegram', 'app_category': 'useful', 'usage_time_seconds': 5124},
            {'app_name': 'YouTube', 'app_category': 'harmful', 'usage_time_seconds': 1524},
            {'app_name': 'TikTok', 'app_category': 'useless', 'usage_time_seconds': 24},
        ]
        
        for app_data in app_usage_data:
            app_data['user'] = request.user
            app_data['date'] = daily_note.date
            AppUsage.objects.get_or_create(
                user=request.user,
                date=daily_note.date,
                app_name=app_data['app_name'],
                defaults=app_data
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DailyNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyNote.objects.filter(user=self.request.user)


class DailyNoteByDateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, date):
        try:
            daily_note = DailyNote.objects.get(user=request.user, date=date)
            serializer = DailyNoteSerializer(daily_note)
            return Response(serializer.data)
        except DailyNote.DoesNotExist:
            return Response({'error': 'Note not found'}, status=404)


# Chat Views
class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            session_id=session_id,
            session__user=self.request.user
        ).order_by('created_at')
    
    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        session = ChatSession.objects.get(id=session_id, user=self.request.user)
        serializer.save(session=session)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)
        
        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            chat_service = ChatGPTService()
            content = serializer.validated_data['content']
            attachments = serializer.validated_data.get('attachments', [])
            
            # Отправляем сообщение в ChatGPT
            response = chat_service.send_message(session_id, content, attachments)
            
            return Response({
                'message': 'Message sent successfully',
                'response': response
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DailyTimelineView(APIView):
    """API для работы с timeline данными"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить timeline данные за конкретную дату"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Сохранить или обновить timeline данные"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Обновляем данные сегментов
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', timeline.sessions_count)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)
    
    def put(self, request):
        """Обновить timeline данные (полная замена)"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Сбрасываем все сегменты
        for i in range(15):
            timeline.set_segment_data(i, 0, 0)
        
        # Заполняем новыми данными
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', 0)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        try:
            file_service = FileUploadService()
            attachment = file_service.upload_file(request.FILES['file'], request.user)
            
            serializer = ChatAttachmentSerializer(attachment)
            return Response(serializer.data, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DailyTimelineView(APIView):
    """API для работы с timeline данными"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить timeline данные за конкретную дату"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Сохранить или обновить timeline данные"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Обновляем данные сегментов
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', timeline.sessions_count)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)
    
    def put(self, request):
        """Обновить timeline данные (полная замена)"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Сбрасываем все сегменты
        for i in range(15):
            timeline.set_segment_data(i, 0, 0)
        
        # Заполняем новыми данными
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', 0)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить профиль текущего пользователя"""
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        """Обновить профиль пользователя"""
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Обновить подписку пользователя"""
        subscription_type = request.data.get('subscription_type', 'free')
        
        if subscription_type not in ['free', 'premium', 'pro']:
            return Response({'error': 'Invalid subscription type'}, status=400)
        
        user = request.user
        user.subscription_type = subscription_type
        user.has_subscription = subscription_type != 'free'
        
        if subscription_type != 'free':
            user.subscription_start_date = timezone.now()
            # Устанавливаем дату окончания на 30 дней
            user.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
        else:
            user.subscription_start_date = None
            user.subscription_end_date = None
        
        user.save()
        
        from .serializers import UserSerializer
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Загрузить аватарку пользователя"""
        try:
            user = request.user
            import os
            from django.conf import settings
            
            # Сохраняем путь к старому файлу для удаления
            old_avatar_path = None
            if user.avatar:
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
            
            # Проверяем, есть ли файл в FILES (обычная загрузка)
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            # Проверяем, есть ли base64 данные в DATA (веб-загрузка)
            elif 'avatar' in request.data and isinstance(request.data['avatar'], str):
                import base64
                from django.core.files.base import ContentFile
                import uuid
                
                avatar_data = request.data['avatar']
                if avatar_data.startswith('data:image'):
                    # Извлекаем base64 данные
                    format, imgstr = avatar_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    # Декодируем base64
                    data = base64.b64decode(imgstr)
                    
                    # Создаем уникальное имя файла
                    filename = f'avatar_{uuid.uuid4().hex[:8]}.{ext}'
                    
                    # Создаем файл
                    avatar_file = ContentFile(data, name=filename)
                    user.avatar = avatar_file
                else:
                    return Response({'error': 'Invalid avatar format'}, status=400)
            else:
                return Response({'error': 'No avatar file provided'}, status=400)
            
            user.save()
            
            # Проверяем, что файл действительно сохранился
            if user.avatar:
                avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
                if not os.path.exists(avatar_path):
                    return Response({'error': 'Failed to save avatar file'}, status=500)
            
            # Удаляем старый файл если он существует
            if old_avatar_path and os.path.exists(old_avatar_path):
                try:
                    os.remove(old_avatar_path)
                    print(f"DEBUG: Удален старый файл аватарки: {old_avatar_path}")
                except Exception as e:
                    print(f"DEBUG: Ошибка удаления старого файла: {e}")
            
            from .serializers import UserSerializer
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DailyTimelineView(APIView):
    """API для работы с timeline данными"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить timeline данные за конкретную дату"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Сохранить или обновить timeline данные"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Обновляем данные сегментов
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', timeline.sessions_count)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)
    
    def put(self, request):
        """Обновить timeline данные (полная замена)"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Сбрасываем все сегменты
        for i in range(15):
            timeline.set_segment_data(i, 0, 0)
        
        # Заполняем новыми данными
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', 0)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request):
        """Удалить аватарку пользователя"""
        try:
            user = request.user
            if user.avatar:
                user.avatar.delete()
            user.avatar = None
            user.save()
            
            from .serializers import UserSerializer
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DailyTimelineView(APIView):
    """API для работы с timeline данными"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить timeline данные за конкретную дату"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Сохранить или обновить timeline данные"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Обновляем данные сегментов
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', timeline.sessions_count)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)
    
    def put(self, request):
        """Обновить timeline данные (полная замена)"""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Получаем или создаем timeline запись
        timeline, created = DailyTimeline.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={}
        )
        
        # Сбрасываем все сегменты
        for i in range(15):
            timeline.set_segment_data(i, 0, 0)
        
        # Заполняем новыми данными
        segments_data = request.data.get('segments', [])
        for segment_data in segments_data:
            index = segment_data.get('index')
            useful_seconds = segment_data.get('useful_seconds', 0)
            harmful_seconds = segment_data.get('harmful_seconds', 0)
            
            if 0 <= index <= 14:
                timeline.set_segment_data(index, useful_seconds, harmful_seconds)
        
        # Обновляем общие счетчики
        timeline.sessions_count = request.data.get('sessions_count', 0)
        timeline.update_totals()
        timeline.save()
        
        serializer = DailyTimelineSerializer(timeline, context={'request': request})
        return Response(serializer.data)