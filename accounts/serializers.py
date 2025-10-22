from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Habit, DailyNote, AppUsage, ChatSession, ChatMessage, ChatAttachment, UserExperience, DailyTimeline, App, AppUsageRecord, UserTestResult, Achievement, AchievementStats

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	avatar_url = serializers.SerializerMethodField()
	level = serializers.SerializerMethodField()
	experience = serializers.SerializerMethodField()
	
	class Meta:
		model = User
		fields = [
			'id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'avatar', 'avatar_url',
			'has_subscription', 'subscription_type', 'subscription_start_date', 
			'subscription_end_date', 'subscription_auto_renew', 'date_joined', 'level', 'experience'
		]
	
	def get_avatar_url(self, obj):
		if obj.avatar:
			# Формируем правильный URL для nginx
			request = self.context.get('request')
			if request:
				return request.build_absolute_uri(obj.avatar.url)
			else:
				# Fallback для случаев без request context
				return f'http://147.45.214.86:8080{obj.avatar.url}'
		return None
	
	def get_level(self, obj):
		# Получаем последнюю запись опыта пользователя
		latest_exp = obj.experience_records.first()
		if latest_exp:
			return latest_exp.level
		return 1
	
	def get_experience(self, obj):
		# Получаем последнюю запись опыта пользователя
		latest_exp = obj.experience_records.first()
		if latest_exp:
			return {
				'total': latest_exp.total_experience,
				'current_level': latest_exp.experience_in_current_level,
				'to_next_level': latest_exp.experience_to_next_level,
				'daily': latest_exp.daily_experience,
				'segments_completed': latest_exp.segments_completed
			}
		return {
			'total': 0,
			'current_level': 0,
			'to_next_level': 1500,
			'daily': 0,
			'segments_completed': 0
		}


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)

	class Meta:
		model = User
		fields = [
			'username', 'first_name', 'last_name', 'email', 'phone_number', 'password'
		]

	def create(self, validated_data):
		password = validated_data.pop('password')
		user = User(**validated_data)
		user.set_password(password)
		user.save()
		return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super().validate(attrs)
		data['user'] = UserSerializer(self.user).data
		return data


class HabitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Habit
		fields = [
			'id', 'name', 'habit_type', 'start_date', 'icon_name'
		]
		read_only_fields = ['id']

	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class AppUsageSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppUsage
		fields = ['app_name', 'app_category', 'usage_time_seconds']
		read_only_fields = ['id']

	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class DailyNoteSerializer(serializers.ModelSerializer):
	app_usage = AppUsageSerializer(many=True, read_only=True)
	
	class Meta:
		model = DailyNote
		fields = [
			'id', 'date', 'mood', 'note', 'app_usage', 'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']

	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class ChatAttachmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChatAttachment
		fields = ['id', 'file', 'file_type', 'file_name', 'file_size', 'created_at']
		read_only_fields = ['id', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
	attachments = ChatAttachmentSerializer(many=True, read_only=True)
	
	class Meta:
		model = ChatMessage
		fields = [
			'id', 'role', 'content', 'created_at', 'has_attachments', 
			'attachment_type', 'attachments'
		]
		read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
	messages = ChatMessageSerializer(many=True, read_only=True)
	message_count = serializers.SerializerMethodField()
	
	class Meta:
		model = ChatSession
		fields = [
			'id', 'title', 'created_at', 'updated_at', 'is_active', 
			'messages', 'message_count'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']
	
	def get_message_count(self, obj):
		return obj.messages.count()
	
	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class SendMessageSerializer(serializers.Serializer):
	content = serializers.CharField(max_length=4000)
	attachments = serializers.ListField(
		child=serializers.IntegerField(),
		required=False,
		allow_empty=True
	)


class UserExperienceSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserExperience
		fields = [
			'date', 'total_experience', 'daily_experience', 'segments_completed',
			'level', 'experience_in_current_level', 'experience_to_next_level'
		]
		read_only_fields = ['level', 'experience_in_current_level', 'experience_to_next_level']
	
	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class DailyTimelineSerializer(serializers.ModelSerializer):
	segments = serializers.SerializerMethodField()
	
	class Meta:
		model = DailyTimeline
		fields = [
			'date', 'segments', 'total_useful_seconds', 'total_harmful_seconds', 
			'total_screen_time_seconds', 'sessions_count', 'created_at', 'updated_at'
		]
		read_only_fields = ['created_at', 'updated_at']
	
	def get_segments(self, obj):
		"""Возвращает данные сегментов в удобном формате"""
		segments = []
		for i in range(15):
			data = obj.get_segment_data(i)
			segments.append({
				'index': i,
				'useful_seconds': data['useful'],
				'harmful_seconds': data['harmful'],
				'total_seconds': data['useful'] + data['harmful']
			})
		return segments
	
	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class AppSerializer(serializers.ModelSerializer):
	"""Сериализатор для модели App"""
	usage_today = serializers.SerializerMethodField()
	usage_week = serializers.SerializerMethodField()
	usage_month = serializers.SerializerMethodField()
	
	class Meta:
		model = App
		fields = [
			'id', 'package_name', 'app_name', 'category', 'icon_base64',
			'first_seen', 'last_used', 'total_usage_seconds', 'is_gpt_classified',
			'usage_today', 'usage_week', 'usage_month'
		]
		read_only_fields = ['id', 'first_seen', 'last_used', 'total_usage_seconds', 'is_gpt_classified']
	
	def get_usage_today(self, obj):
		"""Получить использование за сегодня"""
		from datetime import date
		today = date.today()
		try:
			usage = obj.usage_records.get(date=today)
			return usage.usage_seconds
		except AppUsageRecord.DoesNotExist:
			return 0
	
	def get_usage_week(self, obj):
		"""Получить использование за неделю"""
		from datetime import date, timedelta
		today = date.today()
		week_ago = today - timedelta(days=7)
		usage_records = obj.usage_records.filter(date__gte=week_ago, date__lte=today)
		return sum(record.usage_seconds for record in usage_records)
	
	def get_usage_month(self, obj):
		"""Получить использование за месяц"""
		from datetime import date, timedelta
		today = date.today()
		month_ago = today - timedelta(days=30)
		usage_records = obj.usage_records.filter(date__gte=month_ago, date__lte=today)
		return sum(record.usage_seconds for record in usage_records)


class AppUsageRecordSerializer(serializers.ModelSerializer):
	"""Сериализатор для модели AppUsageRecord"""
	class Meta:
		model = AppUsageRecord
		fields = ['id', 'app', 'date', 'usage_seconds', 'sessions_count']
		read_only_fields = ['id']


class AppCategoryUpdateSerializer(serializers.Serializer):
	"""Сериализатор для обновления категории приложения"""
	category = serializers.ChoiceField(choices=App.CATEGORY_CHOICES)
	
	def validate_category(self, value):
		"""Валидация категории"""
		if value not in [choice[0] for choice in App.CATEGORY_CHOICES]:
			raise serializers.ValidationError("Неверная категория приложения")
		return value


class UserTestResultSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserTestResult
		fields = ['id', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'created_at', 'updated_at']
		read_only_fields = ['id', 'created_at', 'updated_at']


class AchievementSerializer(serializers.ModelSerializer):
	"""Сериализатор для модели Achievement"""
	class Meta:
		model = Achievement
		fields = [
			'id', 'achievement_id', 'title', 'description', 'icon_code_point',
			'icon_font_family', 'icon_font_package', 'achievement_type', 'required_value',
			'is_unlocked', 'unlocked_at', 'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']
	
	def create(self, validated_data):
		validated_data['user'] = self.context['request'].user
		return super().create(validated_data)


class AchievementSyncSerializer(serializers.Serializer):
	"""Сериализатор для синхронизации достижений с клиента"""
	achievements = serializers.ListField(
		child=serializers.DictField(),
		required=True
	)
	
	def validate_achievements(self, value):
		"""Валидация списка достижений"""
		required_fields = ['id', 'title', 'description', 'icon_code_point', 'achievement_type', 'required_value']
		for achievement in value:
			for field in required_fields:
				if field not in achievement:
					raise serializers.ValidationError(f"Отсутствует поле '{field}' в достижении")
		return value


class AchievementStatsSerializer(serializers.ModelSerializer):
	"""Сериализатор для статистики достижений"""
	class Meta:
		model = AchievementStats
		fields = [
			'daily_usage_date', 'consecutive_days', 'ai_chat_usage_count',
			'app_blocking_count', 'low_screen_time_days', 'first_usage_date',
			'total_usage_months', 'last_sync_date', 'created_at'
		]
		read_only_fields = ['last_sync_date', 'created_at']
	
	def create(self, validated_data):
		request = self.context.get('request')
		if not request or not request.user:
			raise serializers.ValidationError("Request context is required")
		
		validated_data['user'] = request.user
		# Получаем или создаем статистику для пользователя
		stats, created = AchievementStats.objects.get_or_create(
			user=validated_data['user'],
			defaults=validated_data
		)
		if not created:
			# Обновляем существующую статистику
			for key, value in validated_data.items():
				setattr(stats, key, value)
			stats.save()
		return stats
