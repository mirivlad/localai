from typing import Dict, Any
from .base import BaseAgent, AgentResult


class OperatorAgent(BaseAgent):
    """Агент для выполнения действий и автоматизации"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="operator",
            model_manager=model_manager,
            tools=["shell", "filesystem", "http"]
        )
        self.system_prompt = """Ты - агент для выполнения действий и автоматизации.
Твоя задача - выполнять команды, управлять файлами и автоматизировать процессы.
Будь осторожен с системными операциями."""
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение операторских задач"""
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
            response_text = await self._call_model(messages, temperature=0.5)
            
            return AgentResult(
                success=True,
                text=response_text,
                agent_name=self.name,
                tools_used=self.tools,
                steps_taken=1,
                metadata={"type": "operation"}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                text=f"Error in OperatorAgent: {str(e)}",
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"error": str(e)}
            )
