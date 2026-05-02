"""
YandexGPT провайдер для локальной агентной платформы
"""
import logging
from typing import Optional, Dict, Any, List
from .base import BaseModelProvider, ModelResponse

logger = logging.getLogger(__name__)


class YandexGPTProvider(BaseModelProvider):
    """Нативный провайдер для YandexGPT"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.folder_id = config.get("folder_id", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "yandexgpt-lite")
        self._client = None
    
    async def _get_client(self):
        """Ленивая инициализация клиента"""
        if self._client is None:
            try:
                from yandex_cloud_ml_sdk import YCloudML
                self._client = YCloudML(
                    folder_id=self.folder_id,
                    auth=self.api_key
                )
                logger.info(f"YandexGPT client initialized: {self.model}")
            except ImportError:
                raise Exception("yandex-cloud-ml-sdk not installed. Run: pip install yandex-cloud-ml-sdk")
            except Exception as e:
                logger.error(f"Failed to initialize YandexGPT: {e}")
                raise
        return self._client
    
    async def generate(self, prompt: str, model: Optional[str] = None, 
                      temperature: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> ModelResponse:
        """Генерация ответа (один промпт)"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model, temperature, max_tokens, **kwargs)
    
    async def chat(self, messages: List[Dict], model: Optional[str] = None,
                   temperature: float = 0.7, max_tokens: int = 1000,
                   **kwargs) -> ModelResponse:
        """Чат с контекстом"""
        client = await self._get_client()
        model_name = model or self.model
        
        try:
            # Получение модели
            model_obj = client.models.completions(model_name)
            
            # Конвертация сообщений
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "text": msg["content"]
                })
            
            # Запрос
            result = await model_obj.run(
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Парсинг ответа
            text = ""
            usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            
            if result and len(result) > 0:
                text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            
            return ModelResponse(
                text=text,
                usage=usage,
                model=model_name
            )
            
        except Exception as e:
            logger.error(f"YandexGPT error: {e}")
            raise Exception(f"YandexGPT error: {str(e)}")
