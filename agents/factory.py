from typing import Dict, Type
from .base import BaseAgent, AgentResult
from .chat_agent import ChatAgent
from .code_agent import CodeAgent
from .operator_agent import OperatorAgent
from .research_agent import ResearchAgent
from .voice_agent import VoiceAgent


class AgentFactory:
    """Фабрика для создания агентов"""
    
    _agent_classes: Dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent,
        "coder": CodeAgent,
        "operator": OperatorAgent,
        "researcher": ResearchAgent,
        "voice": VoiceAgent
    }
    
    @classmethod
    def create_agent(cls, agent_type: str, model_manager=None) -> BaseAgent:
        """Создание агента по типу"""
        agent_class = cls._agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return agent_class(model_manager=model_manager)
    
    @classmethod
    def register_agent(cls, name: str, agent_class: Type[BaseAgent]):
        """Регистрация нового типа агента"""
        cls._agent_classes[name] = agent_class
    
    @classmethod
    def get_available_agents(cls) -> list:
        """Получение списка доступных агентов"""
        return list(cls._agent_classes.keys())
