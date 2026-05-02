from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ModelResponse(BaseModel):
    """Унифицированный ответ от модели"""
    text: str
    usage: Dict[str, Any] = {}
    model: str = "unknown"


class BaseModelProvider(ABC):
    """Базовый класс для провайдеров моделей"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.default_model = config.get("default_model", "")
    
    @abstractmethod
    async def generate(self, prompt: str, model: Optional[str] = None, 
                      temperature: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> ModelResponse:
        """Генерация ответа"""
        pass
    
    @abstractmethod
    async def chat(self, messages: list, model: Optional[str] = None,
                   temperature: float = 0.7, max_tokens: int = 1000,
                   **kwargs) -> ModelResponse:
        """Чат с контекстом"""
        pass
    
    def _normalize_usage(self, usage: Dict) -> Dict[str, Any]:
        """Нормализация статистики использования"""
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
