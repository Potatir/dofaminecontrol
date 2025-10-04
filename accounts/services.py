import openai
import os
from django.conf import settings
from .models import ChatSession, ChatMessage, ChatAttachment
import asyncio
from typing import List, Dict, Optional
import mimetypes


class ChatGPTService:
    def __init__(self):
        # Устанавливаем API ключ глобально
        openai.api_key = settings.OPENAI_API_KEY
    
    def get_session_history(self, session_id: int) -> List[Dict[str, str]]:
        """Получает историю сообщений сессии для отправки в ChatGPT"""
        try:
            session = ChatSession.objects.get(id=session_id)
            messages = session.messages.all().order_by('created_at')
            
            history = []
            for message in messages:
                history.append({
                    "role": message.role,
                    "content": message.content
                })
            
            return history
        except ChatSession.DoesNotExist:
            return []
    
    def process_attachments(self, message: ChatMessage) -> str:
        """Обрабатывает вложения сообщения для ChatGPT"""
        if not message.has_attachments:
            return message.content
        
        content = message.content
        attachments = message.attachments.all()
        
        for attachment in attachments:
            if attachment.file_type == 'image':
                content += f"\n[Изображение: {attachment.file_name}]"
            elif attachment.file_type == 'document':
                content += f"\n[Документ: {attachment.file_name}]"
            else:
                content += f"\n[Файл: {attachment.file_name}]"
        
        return content
    
    def send_message(self, session_id: int, user_message: str, attachment_ids: List[int] = None) -> str:
        """Отправляет сообщение в ChatGPT и возвращает ответ"""
        try:
            # Получаем сессию
            session = ChatSession.objects.get(id=session_id)
            
            # Создаем сообщение пользователя
            user_msg = ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message,
                has_attachments=bool(attachment_ids)
            )
            
            # Добавляем вложения если есть
            if attachment_ids:
                attachments = ChatAttachment.objects.filter(id__in=attachment_ids)
                user_msg.attachments.set(attachments)
                user_msg.attachment_type = 'mixed' if attachments.count() > 1 else attachments.first().file_type
                user_msg.save()
            
            # Получаем историю сообщений
            messages = self.get_session_history(session_id)
            
            # Обрабатываем последнее сообщение с вложениями
            if messages:
                last_message = messages[-1]
                if last_message['role'] == 'user':
                    last_message['content'] = self.process_attachments(user_msg)
            
            # Отправляем в ChatGPT используя старый API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Получаем ответ
            assistant_content = response.choices[0].message.content
            
            # Сохраняем ответ ассистента
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=assistant_content
            )
            
            # Обновляем время последнего обновления сессии
            session.save()
            
            return assistant_content
            
        except ChatSession.DoesNotExist:
            raise ValueError("Сессия чата не найдена")
        except Exception as e:
            raise Exception(f"Ошибка при отправке сообщения: {str(e)}")
    
    def create_session(self, user, title: str = "Новый чат") -> ChatSession:
        """Создает новую сессию чата"""
        return ChatSession.objects.create(
            user=user,
            title=title
        )
    
    def get_user_sessions(self, user) -> List[ChatSession]:
        """Получает все сессии пользователя"""
        return ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at')
    
    def delete_session(self, session_id: int, user) -> bool:
        """Удаляет сессию чата (помечает как неактивную)"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user)
            session.is_active = False
            session.save()
            return True
        except ChatSession.DoesNotExist:
            return False


class FileUploadService:
    def __init__(self):
        self.allowed_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        self.allowed_document_types = ['application/pdf', 'text/plain', 'application/msword']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def get_file_type(self, file) -> str:
        """Определяет тип файла"""
        mime_type, _ = mimetypes.guess_type(file.name)
        
        if mime_type in self.allowed_image_types:
            return 'image'
        elif mime_type in self.allowed_document_types:
            return 'document'
        elif mime_type and mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type and mime_type.startswith('video/'):
            return 'video'
        else:
            return 'other'
    
    def validate_file(self, file) -> tuple[bool, str]:
        """Проверяет файл на валидность"""
        if file.size > self.max_file_size:
            return False, "Файл слишком большой (максимум 10MB)"
        
        mime_type, _ = mimetypes.guess_type(file.name)
        if not mime_type:
            return False, "Неизвестный тип файла"
        
        return True, ""
    
    def upload_file(self, file, user) -> ChatAttachment:
        """Загружает файл и создает запись в БД"""
        is_valid, error = self.validate_file(file)
        if not is_valid:
            raise ValueError(error)
        
        file_type = self.get_file_type(file)
        
        attachment = ChatAttachment.objects.create(
            file=file,
            file_type=file_type,
            file_name=file.name,
            file_size=file.size
        )
        
        return attachment
