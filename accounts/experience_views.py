from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserExperience


class ExperienceView(APIView):
    """API для работы с опытом пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получить текущий опыт пользователя"""
        try:
            from datetime import date
            today = date.today()
            
            # Получаем или создаем запись опыта за сегодня
            experience, created = UserExperience.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    'total_experience': 0,
                    'daily_experience': 0,
                    'segments_completed': 0,
                }
            )
            
            # Если это новая запись, получаем общий опыт из последней записи
            if created:
                last_experience = UserExperience.objects.filter(
                    user=request.user
                ).exclude(date=today).first()
                
                if last_experience:
                    experience.total_experience = last_experience.total_experience
                    experience.save()
            
            return Response({
                'total_experience': experience.total_experience,
                'daily_experience': experience.daily_experience,
                'segments_completed': experience.segments_completed,
                'level': experience.level,
                'experience_in_current_level': experience.experience_in_current_level,
                'experience_to_next_level': experience.experience_to_next_level,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def post(self, request):
        """Начислить опыт за завершенный сегмент"""
        try:
            from datetime import date
            today = date.today()
            
            segment_index = request.data.get('segment_index', 0)
            useful_seconds = request.data.get('useful_seconds', 0)
            harmful_seconds = request.data.get('harmful_seconds', 0)
            experience_earned = request.data.get('experience_earned', 0)
            
            # Получаем или создаем запись опыта за сегодня
            experience, created = UserExperience.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    'total_experience': 0,
                    'daily_experience': 0,
                    'segments_completed': 0,
                }
            )
            
            # Если это новая запись, получаем общий опыт из последней записи
            if created:
                last_experience = UserExperience.objects.filter(
                    user=request.user
                ).exclude(date=today).first()
                
                if last_experience:
                    experience.total_experience = last_experience.total_experience
                    experience.save()
            
            # Начисляем опыт
            experience.daily_experience += experience_earned
            experience.total_experience += experience_earned
            experience.segments_completed += 1
            experience.save()
            
            return Response({
                'success': True,
                'experience_earned': experience_earned,
                'total_experience': experience.total_experience,
                'daily_experience': experience.daily_experience,
                'segments_completed': experience.segments_completed,
                'level': experience.level,
                'experience_in_current_level': experience.experience_in_current_level,
                'experience_to_next_level': experience.experience_to_next_level,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)





