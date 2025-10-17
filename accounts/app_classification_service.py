import openai
from django.conf import settings
from typing import Dict, Any


class AppClassificationService:
    """Сервис для классификации приложений с помощью GPT"""
    
    def __init__(self):
        # Проверяем версию OpenAI и инициализируем соответствующим образом
        try:
            # Для новой версии openai >= 1.0.0
            self.openai_client = openai.OpenAI(
                api_key=getattr(settings, 'OPENAI_API_KEY', '')
            )
        except AttributeError:
            # Для старой версии openai < 1.0.0
            openai.api_key = getattr(settings, 'OPENAI_API_KEY', '')
            self.openai_client = None
    
    def classify_app(self, app_name: str, package_name: str = '') -> Dict[str, Any]:
        """
        Классифицировать приложение на категории: полезное, вредное, бесполезное
        
        Args:
            app_name: Название приложения
            package_name: Имя пакета приложения (опционально)
            
        Returns:
            Dict с результатом классификации
        """
        try:
            # Формируем промпт для GPT
            prompt = self._create_classification_prompt(app_name, package_name)
            
            if self.openai_client:
                # Новая версия API (openai >= 1.0.0)
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты эксперт по анализу мобильных приложений для приложения контроля привычек и цифрового благополучия. Твоя задача - классифицировать приложения на три категории с точки зрения их влияния на продуктивность и формирование здоровых цифровых привычек: полезные, вредные, бесполезные."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                gpt_response = response.choices[0].message.content.strip()
            else:
                # Старая версия API (openai < 1.0.0)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты эксперт по анализу мобильных приложений для приложения контроля привычек и цифрового благополучия. Твоя задача - классифицировать приложения на три категории с точки зрения их влияния на продуктивность и формирование здоровых цифровых привычек: полезные, вредные, бесполезные."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                gpt_response = response.choices[0].message.content.strip()
            
            # Парсим ответ
            classification_result = self._parse_gpt_response(gpt_response)
            
            return {
                'success': True,
                'category': classification_result['category'],
                'confidence': classification_result['confidence'],
                'reasoning': classification_result['reasoning']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'category': 'useless',  # По умолчанию бесполезное
                'confidence': 0.0,
                'reasoning': 'Ошибка при классификации'
            }
    
    def _create_classification_prompt(self, app_name: str, package_name: str) -> str:
        """Создать промпт для классификации приложения"""
        
        prompt = f"""
Проанализируй мобильное приложение и классифицируй его на одну из трех категорий:

НАЗВАНИЕ ПРИЛОЖЕНИЯ: {app_name}
ПАКЕТ: {package_name}

КАТЕГОРИИ:
1. ПОЛЕЗНОЕ - приложения, которые помогают в развитии, обучении, работе, здоровье, продуктивности
2. ВРЕДНОЕ - приложения, которые могут вызывать зависимость, отвлекать, негативно влиять на психику
3. БЕСПОЛЕЗНОЕ - приложения для развлечения, которые не несут особой пользы, но и не вредят

ОТВЕТЬ В ФОРМАТЕ JSON:
{{
    "category": "useful|harmful|useless",
    "confidence": 0.0-1.0,
    "reasoning": "краткое обоснование выбора"
}}

ПРИМЕРЫ:
- Instagram: harmful (социальные сети могут вызывать зависимость)
- Duolingo: useful (обучение языкам)
- Candy Crush: useless (игра для развлечения)
- YouTube: harmful (может вызывать зависимость от просмотра)
- Todoist: useful (планирование и продуктивность)
"""
        return prompt
    
    def _parse_gpt_response(self, response: str) -> Dict[str, Any]:
        """Парсить ответ GPT и извлечь результат классификации"""
        import json
        import re
        
        try:
            # Пытаемся найти JSON в ответе
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Валидируем результат
                category = result.get('category', 'useless')
                if category not in ['useful', 'harmful', 'useless']:
                    category = 'useless'
                
                confidence = float(result.get('confidence', 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Ограничиваем 0-1
                
                reasoning = result.get('reasoning', 'Классификация выполнена')
                
                return {
                    'category': category,
                    'confidence': confidence,
                    'reasoning': reasoning
                }
            else:
                # Если JSON не найден, пытаемся извлечь категорию из текста
                response_lower = response.lower()
                if 'harmful' in response_lower or 'вредное' in response_lower:
                    category = 'harmful'
                elif 'useful' in response_lower or 'полезное' in response_lower:
                    category = 'useful'
                else:
                    category = 'useless'
                
                return {
                    'category': category,
                    'confidence': 0.6,
                    'reasoning': 'Классификация на основе текстового анализа'
                }
                
        except Exception as e:
            return {
                'category': 'useless',
                'confidence': 0.0,
                'reasoning': f'Ошибка парсинга: {str(e)}'
            }
    
    def classify_apps_batch(self, apps_data: list) -> list:
        """
        Классифицировать несколько приложений одновременно
        
        Args:
            apps_data: Список словарей с данными приложений
            
        Returns:
            Список результатов классификации
        """
        results = []
        
        for app_data in apps_data:
            app_name = app_data.get('app_name', '')
            package_name = app_data.get('package_name', '')
            
            result = self.classify_app(app_name, package_name)
            result['app_name'] = app_name
            result['package_name'] = package_name
            
            results.append(result)
        
        return results


# Глобальный экземпляр сервиса
app_classification_service = AppClassificationService()
