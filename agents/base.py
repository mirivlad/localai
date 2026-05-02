from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentResult(BaseModel):
    """Результат работы агента"""
    success: bool
    text: str
    agent_name: str
    tools_used: list = []
    steps_taken: int = 0
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """Базовый класс для всех субагентов"""
    
    def __init__(self, name: str, model_manager=None, tools: Optional[list] = None):
        self.name = name
        self.model_manager = model_manager
        self.tools = tools or []
    
    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение задачи агентом"""
        pass
    
    async def _call_model(self, messages: list, temperature: float = 0.7,
                         max_tokens: int = 1000) -> str:
        """Вызов модели через ModelManager"""
        if not self.model_manager:
            raise Exception("ModelManager not initialized")
        
        response = await self.model_manager.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.text
    
    def add_tool(self, tool: str):
        """Добавление инструмента"""
        if tool not in self.tools:
            self.tools.append(tool)
    
    def get_info(self) -> Dict[str, Any]:
        """Информация об агенте"""
        return {
            "name": self.name,
            "tools": self.tools,
            "type": type(self).__name__
        }
