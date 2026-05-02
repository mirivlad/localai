from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from models import ModelManager, ModelResponse
import json
import re


class RouterOutput(BaseModel):
    """Результат работы роутера"""
    intent: str  # chat, code, action, search, voice
    subagent: str  # chat, coder, operator, researcher, voice
    tools: List[str] = []
    confidence: float = 0.0
    model_preference: str = "local"  # local, cloud, cheap, strong


class Router:
    """LLM-based классификатор для маршрутизации запросов"""
    
    def __init__(self, model_manager: ModelManager, model: Optional[str] = None):
        self.model_manager = model_manager
        self.model = model
        self.system_prompt = """Ты - маршрутизатор запросов. Анализируй запрос пользователя и определи:
1. intent (намерение): chat, code, action, search, voice
2. subagent (какой субагент должен обработать): chat, coder, operator, researcher, voice
3. tools (какие инструменты могут понадобиться): filesystem, shell, http, browser, code_executor
4. confidence (уверенность от 0.0 до 1.0)
5. model_preference (предпочтительный тип модели): local, cloud, cheap, strong

Ответь ТОЛЬКО в формате JSON без дополнительного текста.
Пример: {"intent": "code", "subagent": "coder", "tools": ["filesystem", "shell"], "confidence": 0.95, "model_preference": "strong"}"""

    
    async def route(self, message: str, context: Optional[Dict] = None) -> RouterOutput:
        """Маршрутизация сообщения"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Запрос: {message}"}
        ]
        
        try:
            response: ModelResponse = await self.model_manager.chat(
                messages=messages,
                model=self.model,
                temperature=0.3,
                max_tokens=200
            )
            
            # Парсинг JSON из ответа
            text = response.text.strip()
            # Извлекаем JSON если есть лишний текст
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)
            
            data = json.loads(text)
            
            return RouterOutput(
                intent=data.get("intent", "chat"),
                subagent=data.get("subagent", "chat"),
                tools=data.get("tools", []),
                confidence=data.get("confidence", 0.5),
                model_preference=data.get("model_preference", "local")
            )
        
        except Exception as e:
            # Fallback на простую эвристику
            return self._fallback_route(message)
    
    def _fallback_route(self, message: str) -> RouterOutput:
        """Простая эвристика если LLM недоступен"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["код", "code", "напиши", "write", "функция", "function"]):
            return RouterOutput(
                intent="code",
                subagent="coder",
                tools=["filesystem", "shell"],
                confidence=0.7,
                model_preference="strong"
            )
        elif any(word in message_lower for word in ["поиск", "search", "найди", "find", "google"]):
            return RouterOutput(
                intent="search",
                subagent="researcher",
                tools=["http", "browser"],
                confidence=0.7,
                model_preference="cloud"
            )
        elif any(word in message_lower for word in ["выполни", "execute", "запусти", "run"]):
            return RouterOutput(
                intent="action",
                subagent="operator",
                tools=["shell", "filesystem"],
                confidence=0.7,
                model_preference="local"
            )
        else:
            return RouterOutput(
                intent="chat",
                subagent="chat",
                tools=[],
                confidence=0.8,
                model_preference="local"
            )
