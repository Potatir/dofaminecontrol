from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    MeView,
    FlexibleTokenObtainPairView,
    SmsRequestCodeView,
    SmsVerifyCodeView,
    SocialLoginStubView,
    FirebasePhoneLoginView,
    DeleteAccountView,
    TestResultView,
    HabitListCreateView,
    HabitDetailView,
    HabitResetView,
    DailyNoteListCreateView,
    DailyNoteDetailView,
    DailyNoteByDateView,
    ChatSessionListCreateView,
    ChatSessionDetailView,
    MessageListCreateView,
    SendMessageView,
    FileUploadView,
    UserProfileView,
    UserSubscriptionView,
    UserAvatarView,
    DailyTimelineView,
)
from .achievement_views import (
    AchievementListView,
    AchievementSyncView,
    AchievementStatsView,
)
from .app_views import (
    get_user_apps,
    get_app_details,
    create_or_update_app,
    update_app_category,
    update_app_usage,
)
from .experience_views import ExperienceView


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', FlexibleTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    # SMS authentication
    path('auth/sms/send/', SmsRequestCodeView.as_view(), name='auth-sms-send'),
    path('auth/sms/verify/', SmsVerifyCodeView.as_view(), name='auth-sms-verify'),
    # Social authentication
    path('auth/google/', SocialLoginStubView.as_view(), name='auth-google'),
    path('auth/social/<str:provider>/', SocialLoginStubView.as_view(), name='auth-social-stub'),
    # Firebase Phone Authentication
    path('auth/firebase/phone/', FirebasePhoneLoginView.as_view(), name='auth-firebase-phone'),
    # Delete account
    path('auth/delete-account/', DeleteAccountView.as_view(), name='auth-delete-account'),
    # Test results
    path('test-results/', TestResultView.as_view(), name='test-results'),
    # Habits
    path('habits/', HabitListCreateView.as_view(), name='habit-list-create'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('habits/<int:pk>/reset/', HabitResetView.as_view(), name='habit-reset'),
    # Daily Notes
    path('daily-notes/', DailyNoteListCreateView.as_view(), name='daily-note-list-create'),
    path('daily-notes/<int:pk>/', DailyNoteDetailView.as_view(), name='daily-note-detail'),
    path('daily-notes/date/<str:date>/', DailyNoteByDateView.as_view(), name='daily-note-by-date'),
    # Chat
    path('chat/sessions/', ChatSessionListCreateView.as_view(), name='chat-session-list'),
    path('chat/sessions/<int:pk>/', ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('chat/sessions/<int:session_id>/messages/', MessageListCreateView.as_view(), name='chat-message-list'),
    path('chat/sessions/<int:session_id>/send/', SendMessageView.as_view(), name='chat-send-message'),
    path('chat/upload/', FileUploadView.as_view(), name='chat-file-upload'),
    # User Profile
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/subscription/', UserSubscriptionView.as_view(), name='user-subscription'),
    path('user/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    # Timeline
    path('timeline/', DailyTimelineView.as_view(), name='timeline'),
    path('experience/', ExperienceView.as_view(), name='experience'),
    # Apps
    path('apps/', get_user_apps, name='user-apps'),
    path('apps/<int:app_id>/', get_app_details, name='app-details'),
    path('apps/create/', create_or_update_app, name='create-or-update-app'),
    path('apps/<int:app_id>/category/', update_app_category, name='update-app-category'),
    path('apps/<int:app_id>/usage/', update_app_usage, name='update-app-usage'),
    # Achievements
    path('achievements/', AchievementListView.as_view(), name='achievement-list'),
    path('achievements/sync/', AchievementSyncView.as_view(), name='achievement-sync'),
    path('achievements/stats/', AchievementStatsView.as_view(), name='achievement-stats'),
]


