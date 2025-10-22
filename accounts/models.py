from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Подписка
    has_subscription = models.BooleanField(default=False)
    subscription_type = models.CharField(
        max_length=20, 
        choices=[
            ('free', 'Базовая'),
            ('premium', 'Премиум'),
            ('pro', 'Премиум'),
        ],
        default='free'
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    subscription_auto_renew = models.BooleanField(default=False)


class UserTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    question_1 = models.CharField(max_length=200, blank=True, null=True)  # Что важнее прямо сейчас?
    question_2 = models.CharField(max_length=200, blank=True, null=True)
    question_3 = models.CharField(max_length=200, blank=True, null=True)
    question_4 = models.CharField(max_length=200, blank=True, null=True)
    question_5 = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class Habit(models.Model):
    HABIT_TYPES = [
        ('bad', 'Плохая привычка'),
        ('good', 'Хорошая привычка'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    habit_type = models.CharField(max_length=10, choices=HABIT_TYPES)
    start_date = models.DateTimeField(default=timezone.now)
    icon_name = models.CharField(max_length=50, default='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class DailyNote(models.Model):
    MOOD_CHOICES = [
        (1, 'Очень плохо'),
        (2, 'Плохо'),
        (3, 'Нормально'),
        (4, 'Хорошо'),
        (5, 'Отлично'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_notes')
    date = models.DateField()
    mood = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']


class AppUsage(models.Model):
    CATEGORY_CHOICES = [
        ('useful', 'Полезное'),
        ('harmful', 'Вредное'),
        ('useless', 'Бесполезное'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_usage')
    date = models.DateField()
    app_name = models.CharField(max_length=100)
    app_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    usage_time_seconds = models.IntegerField()  # Время в секундах
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date', 'app_name']
        ordering = ['-usage_time_seconds']


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="Новый чат")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('system', 'Система'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    has_attachments = models.BooleanField(default=False)
    attachment_type = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']


class ChatAttachment(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('document', 'Документ'),
        ('audio', 'Аудио'),
        ('video', 'Видео'),
        ('other', 'Другое'),
    ]
    
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_attachments/%Y/%m/%d/')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class UserExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experience_records')
    date = models.DateField()
    total_experience = models.IntegerField(default=0)  # Общий опыт пользователя
    daily_experience = models.IntegerField(default=0)  # Опыт за конкретный день
    segments_completed = models.IntegerField(default=0)  # Количество завершенных сегментов
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    @property
    def level(self):
        """Вычисляет уровень на основе общего опыта"""
        if self.total_experience < 1500:
            return 1
        
        exp = self.total_experience
        level = 1
        required_exp = 1500
        
        while exp >= required_exp:
            exp -= required_exp
            level += 1
            required_exp = int(required_exp * 1.5)
        
        return level
    
    @property
    def experience_to_next_level(self):
        """Опыт, необходимый для следующего уровня"""
        if self.total_experience < 1500:
            return 1500 - self.total_experience
        
        exp = self.total_experience
        level = 1
        required_exp = 1500
        
        while exp >= required_exp:
            exp -= required_exp
            level += 1
            required_exp = int(required_exp * 1.5)
        
        return required_exp - exp
    
    @property
    def experience_in_current_level(self):
        """Опыт в текущем уровне"""
        if self.total_experience < 1500:
            return self.total_experience
        
        exp = self.total_experience
        level = 1
        required_exp = 1500
        
        while exp >= required_exp:
            exp -= required_exp
            level += 1
            required_exp = int(required_exp * 1.5)
        
        return exp


class App(models.Model):
    """Модель для хранения информации о приложениях"""
    CATEGORY_CHOICES = [
        ('useful', 'Полезное'),
        ('harmful', 'Вредное'),
        ('useless', 'Бесполезное'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apps')
    package_name = models.CharField(max_length=255)  # Например: com.example.app
    app_name = models.CharField(max_length=255)  # Отображаемое имя приложения
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='useless')
    icon_base64 = models.TextField(blank=True, null=True)  # Base64 иконка
    first_seen = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    total_usage_seconds = models.IntegerField(default=0)  # Общее время использования
    is_gpt_classified = models.BooleanField(default=False)  # Было ли классифицировано GPT
    
    class Meta:
        unique_together = ['user', 'package_name']
        ordering = ['-last_used']
    
    def __str__(self):
        return f"{self.user.username} - {self.app_name} ({self.category})"


class AppUsageRecord(models.Model):
    """Модель для детального отслеживания использования приложений"""
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='usage_records')
    date = models.DateField()
    usage_seconds = models.IntegerField(default=0)
    sessions_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['app', 'date']
        ordering = ['-date']


class DailyTimeline(models.Model):
    """Модель для хранения данных о времени использования по сегментам дня"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_timelines')
    date = models.DateField()
    
    # 15 сегментов по ~1.6 часа каждый (0-14)
    segment_0_useful = models.IntegerField(default=0)
    segment_0_harmful = models.IntegerField(default=0)
    segment_1_useful = models.IntegerField(default=0)
    segment_1_harmful = models.IntegerField(default=0)
    segment_2_useful = models.IntegerField(default=0)
    segment_2_harmful = models.IntegerField(default=0)
    segment_3_useful = models.IntegerField(default=0)
    segment_3_harmful = models.IntegerField(default=0)
    segment_4_useful = models.IntegerField(default=0)
    segment_4_harmful = models.IntegerField(default=0)
    segment_5_useful = models.IntegerField(default=0)
    segment_5_harmful = models.IntegerField(default=0)
    segment_6_useful = models.IntegerField(default=0)
    segment_6_harmful = models.IntegerField(default=0)
    segment_7_useful = models.IntegerField(default=0)
    segment_7_harmful = models.IntegerField(default=0)
    segment_8_useful = models.IntegerField(default=0)
    segment_8_harmful = models.IntegerField(default=0)
    segment_9_useful = models.IntegerField(default=0)
    segment_9_harmful = models.IntegerField(default=0)
    segment_10_useful = models.IntegerField(default=0)
    segment_10_harmful = models.IntegerField(default=0)
    segment_11_useful = models.IntegerField(default=0)
    segment_11_harmful = models.IntegerField(default=0)
    segment_12_useful = models.IntegerField(default=0)
    segment_12_harmful = models.IntegerField(default=0)
    segment_13_useful = models.IntegerField(default=0)
    segment_13_harmful = models.IntegerField(default=0)
    segment_14_useful = models.IntegerField(default=0)
    segment_14_harmful = models.IntegerField(default=0)
    
    # Общая статистика
    total_useful_seconds = models.IntegerField(default=0)
    total_harmful_seconds = models.IntegerField(default=0)
    total_screen_time_seconds = models.IntegerField(default=0)
    sessions_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def get_segment_data(self, segment_index):
        """Получить данные для конкретного сегмента"""
        if not 0 <= segment_index <= 14:
            return {'useful': 0, 'harmful': 0}
        
        useful_field = f'segment_{segment_index}_useful'
        harmful_field = f'segment_{segment_index}_harmful'
        
        return {
            'useful': getattr(self, useful_field),
            'harmful': getattr(self, harmful_field)
        }
    
    def set_segment_data(self, segment_index, useful_seconds, harmful_seconds):
        """Установить данные для конкретного сегмента"""
        if not 0 <= segment_index <= 14:
            return
        
        useful_field = f'segment_{segment_index}_useful'
        harmful_field = f'segment_{segment_index}_harmful'
        
        setattr(self, useful_field, useful_seconds)
        setattr(self, harmful_field, harmful_seconds)
    
    def update_totals(self):
        """Обновить общие счетчики на основе данных сегментов"""
        total_useful = 0
        total_harmful = 0
        
        for i in range(15):
            data = self.get_segment_data(i)
            total_useful += data['useful']
            total_harmful += data['harmful']
        
        self.total_useful_seconds = total_useful
        self.total_harmful_seconds = total_harmful
        self.total_screen_time_seconds = total_useful + total_harmful


class Achievement(models.Model):
    """Модель для хранения достижений пользователя"""
    ACHIEVEMENT_TYPES = [
        ('daily_streak', 'Ежедневная серия'),
        ('ai_chat_usage', 'Использование ИИ чата'),
        ('app_blocking', 'Блокировка приложений'),
        ('low_screen_time', 'Низкое экранное время'),
        ('total_usage_months', 'Общее использование (месяцы)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_id = models.CharField(max_length=100)  # ID достижения из Flutter
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_code_point = models.IntegerField()  # Код иконки из Flutter
    icon_font_family = models.CharField(max_length=100, blank=True, null=True)
    icon_font_package = models.CharField(max_length=100, blank=True, null=True)
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    required_value = models.IntegerField()  # Необходимое значение для разблокировки
    is_unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'achievement_id']
        ordering = ['-unlocked_at', 'achievement_type', 'required_value']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Разблокировано' if self.is_unlocked else 'Заблокировано'})"


class AchievementStats(models.Model):
    """Модель для хранения статистики достижений пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_stats')
    
    # Статистика ежедневного использования
    daily_usage_date = models.DateField(null=True, blank=True)
    consecutive_days = models.IntegerField(default=0)
    
    # Статистика использования функций
    ai_chat_usage_count = models.IntegerField(default=0)
    app_blocking_count = models.IntegerField(default=0)
    low_screen_time_days = models.IntegerField(default=0)
    
    # Общая статистика
    first_usage_date = models.DateTimeField(null=True, blank=True)
    total_usage_months = models.IntegerField(default=0)
    
    # Последнее обновление
    last_sync_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user']
    
    def __str__(self):
        return f"{self.user.username} - Achievement Stats"