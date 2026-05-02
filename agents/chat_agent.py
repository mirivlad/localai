from typing import Dict, Any
from .base import BaseAgent, AgentResult


class ChatAgent(BaseAgent):
    """Агент для диалога и объяснений"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="chat",
            model_manager=model_manager,
            tools=[]  # Чат-агент обычно не использует инструменты
        )
        self.system_prompt = """Ты - полезный помощник для диалога.
Отвечай вежливо, информативно и по существу.
Используй контекст разговора для поддержания связности диалога."""
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение диалогового запроса"""
        message = context.get("message", "")
        history = context.get("short_term_history", [])
        
        # Сборка сообщений
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Добавляем историю
        for hist in history:
            messages.append({
                "role": hist.get("role", "user"),
                "content": hist.get("content", "")
            })
        
        # Добавляем текущий запрос
        messages.append({"role": "user", "content": message})
        
        try:
            response_text = await self._call_model(messages, temperature=0.7)
            
            return AgentResult(
                success=True,
                text=response_text,
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"type": "chat"}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                text=f"Error in ChatAgent: {str(e)}",
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"error": str(e)}
            )
