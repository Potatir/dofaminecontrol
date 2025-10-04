from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import App, AppUsageRecord
from .serializers import AppSerializer, AppCategoryUpdateSerializer
from .app_classification_service import app_classification_service


# API для работы с приложениями
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_apps(request):
    """Получить все приложения пользователя"""
    apps = App.objects.filter(user=request.user)
    serializer = AppSerializer(apps, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_app_details(request, app_id):
    """Получить детальную информацию о приложении"""
    try:
        app = App.objects.get(id=app_id, user=request.user)
        serializer = AppSerializer(app, context={'request': request})
        return Response(serializer.data)
    except App.DoesNotExist:
        return Response(
            {'error': 'Приложение не найдено'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_app(request):
    """Создать новое приложение или обновить существующее"""
    package_name = request.data.get('package_name')
    app_name = request.data.get('app_name')
    icon_base64 = request.data.get('icon_base64', '')
    
    if not package_name or not app_name:
        return Response(
            {'error': 'Требуются package_name и app_name'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Создаем или получаем существующее приложение
    app, created = App.objects.get_or_create(
        user=request.user,
        package_name=package_name,
        defaults={
            'app_name': app_name,
            'icon_base64': icon_base64,
            'category': 'useless'  # По умолчанию бесполезное
        }
    )
    
    # Если приложение новое и еще не классифицировано, классифицируем его
    if created and not app.is_gpt_classified:
        try:
            classification_result = app_classification_service.classify_app(app_name, package_name)
            if classification_result['success']:
                app.category = classification_result['category']
                app.is_gpt_classified = True
                app.save()
        except Exception as e:
            # В случае ошибки классификации оставляем приложение как бесполезное
            pass
    
    if not created:
        # Обновляем существующее приложение
        app.app_name = app_name
        if icon_base64:
            app.icon_base64 = icon_base64
        app.last_used = timezone.now()
        app.save()
    
    serializer = AppSerializer(app, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_app_category(request, app_id):
    """Обновить категорию приложения"""
    try:
        app = App.objects.get(id=app_id, user=request.user)
        serializer = AppCategoryUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            app.category = serializer.validated_data['category']
            app.save()
            
            app_serializer = AppSerializer(app, context={'request': request})
            return Response(app_serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except App.DoesNotExist:
        return Response(
            {'error': 'Приложение не найдено'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_app_usage(request, app_id):
    """Обновить статистику использования приложения"""
    try:
        app = App.objects.get(id=app_id, user=request.user)
        usage_date = request.data.get('date', timezone.now().date())
        usage_seconds = request.data.get('usage_seconds', 0)
        sessions_count = request.data.get('sessions_count', 1)
        
        # Создаем или обновляем запись использования
        usage_record, created = AppUsageRecord.objects.get_or_create(
            app=app,
            date=usage_date,
            defaults={
                'usage_seconds': usage_seconds,
                'sessions_count': sessions_count
            }
        )
        
        if not created:
            usage_record.usage_seconds += usage_seconds
            usage_record.sessions_count += sessions_count
            usage_record.save()
        
        # Обновляем общую статистику приложения
        app.total_usage_seconds += usage_seconds
        app.last_used = timezone.now()
        app.save()
        
        return Response({'status': 'success'})
        
    except App.DoesNotExist:
        return Response(
            {'error': 'Приложение не найдено'}, 
            status=status.HTTP_404_NOT_FOUND
        )
