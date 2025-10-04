from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Achievement, AchievementStats


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone_number")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "phone_number", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "email", "phone_number", "first_name", "last_name", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "phone_number")
    ordering = ("id",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_id', 'title', 'achievement_type', 'is_unlocked', 'unlocked_at', 'created_at')
    list_filter = ('achievement_type', 'is_unlocked', 'created_at')
    search_fields = ('user__username', 'title', 'achievement_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-unlocked_at', 'achievement_type', 'required_value')


@admin.register(AchievementStats)
class AchievementStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'consecutive_days', 'ai_chat_usage_count', 'app_blocking_count', 'low_screen_time_days', 'last_sync_date')
    list_filter = ('last_sync_date', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('last_sync_date', 'created_at')
    ordering = ('-last_sync_date',)

