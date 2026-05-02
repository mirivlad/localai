from typing import Dict, Any, Optional, List
from .base import BaseModelProvider, ModelResponse
from .openai_compatible import OpenAICompatibleProvider


class ModelManager:
    """Менеджер моделей - выбор провайдера, fallback, нормализация"""
    
    def __init__(self):
        self.providers: Dict[str, BaseModelProvider] = {}
        self.fallback_chain: List[str] = []
    
    def register_provider(self, provider: BaseModelProvider):
        """Регистрация провайдера"""
        self.providers[provider.name] = provider
    
    def set_fallback_chain(self, chain: List[str]):
        """Установка цепочки fallback провайдеров"""
        self.fallback_chain = chain
    
    async def generate(self, prompt: str, 
                      provider_name: Optional[str] = None,
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: int = 1000,
                      **kwargs) -> ModelResponse:
        """Генерация с автоматическим выбором провайдера или fallback"""
        
        # Если указан конкретный провайдер
        if provider_name and provider_name in self.providers:
            return await self._call_provider(
                self.providers[provider_name], prompt, None, 
                model, temperature, max_tokens, **kwargs
            )
        
        # Пробуем цепочку fallback
        errors = []
        for name in self.fallback_chain:
            if name in self.providers:
                try:
                    return await self._call_provider(
                        self.providers[name], prompt, None,
                        model, temperature, max_tokens, **kwargs
                    )
                except Exception as e:
                    errors.append(f"{name}: {str(e)}")
        
        raise Exception(f"All providers failed. Errors: {errors}")
    
    async def chat(self, messages: list,
                  provider_name: Optional[str] = None,
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: int = 1000,
                  **kwargs) -> ModelResponse:
        """Чат с автоматическим выбором провайдера"""
        
        if provider_name and provider_name in self.providers:
            return await self._call_provider_chat(
                self.providers[provider_name], messages,
                model, temperature, max_tokens, **kwargs
            )
        
        errors = []
        for name in self.fallback_chain:
            if name in self.providers:
                try:
                    return await self._call_provider_chat(
                        self.providers[name], messages,
                        model, temperature, max_tokens, **kwargs
                    )
                except Exception as e:
                    errors.append(f"{name}: {str(e)}")
        
        raise Exception(f"All providers failed. Errors: {errors}")
    
    async def _call_provider(self, provider: BaseModelProvider, 
                            prompt: str, *args, **kwargs) -> ModelResponse:
        return await provider.generate(prompt, *args, **kwargs)
    
    async def _call_provider_chat(self, provider: BaseModelProvider,
                                 messages: list, *args, **kwargs) -> ModelResponse:
        return await provider.chat(messages, *args, **kwargs)
    
    def get_provider_info(self) -> List[Dict[str, Any]]:
        """Информация о зарегистрированных провайдерах"""
        return [
            {
                "name": p.name,
                "type": type(p).__name__,
                "model": p.default_model,
                "base_url": p.base_url
            }
            for p in self.providers.values()
        ]
