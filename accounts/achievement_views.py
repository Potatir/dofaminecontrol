from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Achievement, AchievementStats
from .serializers import AchievementSerializer, AchievementSyncSerializer, AchievementStatsSerializer


class AchievementListView(generics.ListAPIView):
    """Получить все достижения пользователя"""
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)


class AchievementSyncView(APIView):
    """Синхронизация достижений с клиента"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AchievementSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        achievements_data = serializer.validated_data['achievements']
        user = request.user
        
        # Синхронизируем каждое достижение
        synced_achievements = []
        for achievement_data in achievements_data:
            # Преобразуем данные из Flutter формата в Django формат
            django_achievement_data = {
                'achievement_id': achievement_data['id'],
                'title': achievement_data['title'],
                'description': achievement_data['description'],
                'icon_code_point': achievement_data['icon_code_point'],
                'icon_font_family': achievement_data.get('icon_font_family'),
                'icon_font_package': achievement_data.get('icon_font_package'),
                'achievement_type': achievement_data['type'],
                'required_value': achievement_data['required_value'],
                'is_unlocked': achievement_data.get('is_unlocked', False),
                'unlocked_at': achievement_data.get('unlocked_at'),
            }
            
            # Получаем или создаем достижение
            achievement, created = Achievement.objects.get_or_create(
                user=user,
                achievement_id=achievement_data['id'],
                defaults=django_achievement_data
            )
            
            # Если достижение уже существует, обновляем его
            if not created:
                for key, value in django_achievement_data.items():
                    setattr(achievement, key, value)
                achievement.save()
            
            synced_achievements.append(achievement)
        
        # Возвращаем обновленные достижения
        serializer = AchievementSerializer(synced_achievements, many=True, context={'request': request})
        return Response(serializer.data)


class AchievementStatsView(APIView):
    """Синхронизация статистики достижений"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AchievementStatsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        stats = serializer.save()
        return Response(AchievementStatsSerializer(stats).data)
    
    def get(self, request):
        """Получить текущую статистику пользователя"""
        try:
            stats = AchievementStats.objects.get(user=request.user)
            serializer = AchievementStatsSerializer(stats)
            return Response(serializer.data)
        except AchievementStats.DoesNotExist:
            # Создаем пустую статистику если её нет
            stats = AchievementStats.objects.create(user=request.user)
            serializer = AchievementStatsSerializer(stats)
            return Response(serializer.data)
