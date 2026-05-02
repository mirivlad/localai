"""
GigaChat провайдер для локальной агентной платформы
"""
import logging
from typing import Optional, Dict, Any, List
from .base import BaseModelProvider, ModelResponse

logger = logging.getLogger(__name__)


class GigaChatProvider(BaseModelProvider):
    """Нативный провайдер для GigaChat"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.profile = config.get("profile", "default")
        self.model = config.get("model", "GigaChat-Pro")
        self._client = None
    
    async def _get_client(self):
        """Ленивая инициализация клиента"""
        if self._client is None:
            try:
                from gigachat import GigaChat
                self._client = GigaChat(
                    credentials=f"{self.client_id}:{self.client_secret}",
                    scope=self.profile,
                    model=self.model
                )
                logger.info(f"GigaChat client initialized: {self.model}")
            except ImportError:
                raise Exception("gigachat library not installed. Run: pip install gigachat")
            except Exception as e:
                logger.error(f"Failed to initialize GigaChat: {e}")
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
            # Конвертация сообщений в формат GigaChat
            from gigachat.models import Messages, MessagesRole
            
            gc_messages = []
            for msg in messages:
                role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
                gc_messages.append(Messages(role=role, content=msg["content"]))
            
            # Запрос
            from gigachat.models import Chat, CompletionsOptions
            
            chat = Chat(
                messages=gc_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model_name
            )
            
            response = await client.achat(chat)
            
            return ModelResponse(
                text=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model=response.model or model_name
            )
            
        except Exception as e:
            logger.error(f"GigaChat error: {e}")
            raise Exception(f"GigaChat error: {str(e)}")
