from typing import Dict, Any
from .base import BaseAgent, AgentResult


class CodeAgent(BaseAgent):
    """Агент для генерации и анализа кода"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="coder",
            model_manager=model_manager,
            tools=["filesystem", "shell", "code_executor"]
        )
        self.system_prompt = """Ты - эксперт программист.
Твоя задача - писать, анализировать и исправлять код.
Предоставляй чистый, хорошо документированный код.
Используй markdown для форматирования кода."""
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение задачи программирования"""
        message = context.get("message", "")
        history = context.get("short_term_history", [])
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for hist in history:
            messages.append({
                "role": hist.get("role", "user"),
                "content": hist.get("content", "")
            })
        
        messages.append({"role": "user", "content": message})
        
        try:
            response_text = await self._call_model(messages, temperature=0.3)
            
            return AgentResult(
                success=True,
                text=response_text,
                agent_name=self.name,
                tools_used=self.tools,
                steps_taken=1,
                metadata={"type": "code"}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                text=f"Error in CodeAgent: {str(e)}",
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"error": str(e)}
            )
