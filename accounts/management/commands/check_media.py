from django.core.management.base import BaseCommand
from django.conf import settings
import os
from accounts.models import User

class Command(BaseCommand):
    help = 'Проверяет и исправляет медиа файлы'

    def handle(self, *args, **options):
        self.stdout.write('Проверяем медиа файлы...')
        
        # Создаем папку avatars если её нет
        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)
            self.stdout.write(f'Создана папка: {avatars_dir}')
        
        # Проверяем пользователей с аватарками
        users_with_avatars = User.objects.exclude(avatar='')
        self.stdout.write(f'Найдено пользователей с аватарками: {users_with_avatars.count()}')
        
        cleaned_count = 0
        for user in users_with_avatars:
            if user.avatar:
                avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
                if os.path.exists(avatar_path):
                    self.stdout.write(f'✓ Аватарка пользователя {user.username}: {avatar_path}')
                else:
                    self.stdout.write(f'✗ Аватарка пользователя {user.username} не найдена: {avatar_path}')
                    # Очищаем поле avatar если файл не существует
                    user.avatar = ''
                    user.save()
                    cleaned_count += 1
                    self.stdout.write(f'  Очищено поле avatar для пользователя {user.username}')
        
        # Показываем статистику файлов в папке
        if os.path.exists(avatars_dir):
            files_in_dir = os.listdir(avatars_dir)
            self.stdout.write(f'Файлов в папке avatars: {len(files_in_dir)}')
            for file in files_in_dir[:5]:  # Показываем первые 5 файлов
                self.stdout.write(f'  - {file}')
            if len(files_in_dir) > 5:
                self.stdout.write(f'  ... и еще {len(files_in_dir) - 5} файлов')
        
        self.stdout.write(f'Проверка завершена! Очищено записей: {cleaned_count}')
