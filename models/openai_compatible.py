import openai
from typing import Optional, Dict, Any, List
from .base import BaseModelProvider, ModelResponse


class OpenAICompatibleProvider(BaseModelProvider):
    """Провайдер совместимый с OpenAI API"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.client = openai.AsyncOpenAI(
            base_url=self.base_url if self.base_url else None,
            api_key=self.api_key if self.api_key else "sk-no-key-required"
        )
    
    async def generate(self, prompt: str, model: Optional[str] = None,
                      temperature: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> ModelResponse:
        """Генерация ответа (один промпт)"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model, temperature, max_tokens, **kwargs)
    
    async def chat(self, messages: List[Dict], model: Optional[str] = None,
                   temperature: float = 0.7, max_tokens: int = 1000,
                   **kwargs) -> ModelResponse:
        """Чат с историей сообщений"""
        model_name = model or self.default_model
        
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            text = response.choices[0].message.content
            usage = self._normalize_usage(response.usage.model_dump())
            model_used = response.model
            
            return ModelResponse(text=text, usage=usage, model=model_used)
        
        except Exception as e:
            # Логирование ошибки должно быть добавлено позже
            raise Exception(f"Provider {self.name} error: {str(e)}")
