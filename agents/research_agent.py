from typing import Dict, Any
from .base import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    """Агент для поиска и анализа информации"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="researcher",
            model_manager=model_manager,
            tools=["http", "browser"]
        )
        self.system_prompt = """Ты - исследовательский агент.
Твоя задача - искать информацию, анализировать источники и предоставлять структурированные ответы.
Всегда проверяй факты и указывай источники."""
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение исследовательской задачи"""
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
            response_text = await self._call_model(messages, temperature=0.7)
            
            return AgentResult(
                success=True,
                text=response_text,
                agent_name=self.name,
                tools_used=self.tools,
                steps_taken=1,
                metadata={"type": "research"}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                text=f"Error in ResearchAgent: {str(e)}",
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"error": str(e)}
            )
