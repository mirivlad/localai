from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Результат выполнения инструмента"""
    success: bool
    output: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseTool(ABC):
    """Базовый класс для инструментов"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Выполнение инструмента"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Информация об инструменте"""
        return {
            "name": self.name,
            "description": self.description,
            "type": type(self).__name__
        }
