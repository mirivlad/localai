from typing import Dict, Any
from .base import BaseAgent, AgentResult


class VoiceAgent(BaseAgent):
    """Агент для голосового взаимодействия"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="voice",
            model_manager=model_manager,
            tools=[]  # VoiceAgent координирует STT/TTS
        )
        self.system_prompt = """Ты - голосовой ассистент.
Отвечай кратко и естественно, как в живом разговоре.
Используй разговорный стиль речи."""
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """Выполнение голосового запроса"""
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
            response_text = await self._call_model(messages, temperature=0.8)
            
            return AgentResult(
                success=True,
                text=response_text,
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"type": "voice"}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                text=f"Error in VoiceAgent: {str(e)}",
                agent_name=self.name,
                tools_used=[],
                steps_taken=1,
                metadata={"error": str(e)}
            )
