from typing import Dict, Any, Optional, List
from .router import Router, RouterOutput
from .context_builder import ContextBuilder
from .state_tracker import StateTracker
from models import ModelManager


class ExecutionManager:
    """Управление выполнением запросов"""
    
    def __init__(self, model_manager: ModelManager, 
                 max_steps: int = 5, timeout: int = 60):
        self.model_manager = model_manager
        self.max_steps = max_steps
        self.timeout = timeout
        self.router = Router(model_manager)
        self.context_builder = ContextBuilder()
        self.state_tracker = StateTracker()
    
    async def execute(self, session_id: str, message: str) -> Dict[str, Any]:
        """Выполнение запроса через оркестрацию"""
        
        # 1. Роутинг
        router_output: RouterOutput = await self.router.route(message)
        self.state_tracker.log_routing(session_id, message, router_output)
        
        # 2. Сбор контекста
        context = self.context_builder.build_context(
            session_id=session_id,
            message=message,
            router_output=router_output
        )
        
        # 3. Выбор модели на основе предпочтений роутера
        model_name = self._select_model(router_output.model_preference)
        
        # 4. Выполнение через субагента (пока заглушка - прямой вызов модели)
        response = await self._execute_with_model(
            session_id=session_id,
            context=context,
            model_name=model_name
        )
        
        # 5. Обновление истории
        self.context_builder.add_to_history("user", message)
        self.context_builder.add_to_history("assistant", response["text"])
        
        return {
            "session_id": session_id,
            "text": response["text"],
            "model": response["model"],
            "usage": response["usage"],
            "router": router_output.dict(),
            "tools_used": router_output.tools
        }
    
    async def _execute_with_model(self, session_id: str, 
                                  context: Dict, model_name: Optional[str]) -> Dict:
        """Выполнение с использованием модели"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": context["message"]}
        ]
        
        # Добавляем историю если есть
        for hist in context.get("short_term_history", []):
            messages.insert(-1, hist)
        
        response = await self.model_manager.chat(
            messages=messages,
            model=model_name
        )
        
        self.state_tracker.log_model_call(
            session_id=session_id,
            provider="unknown",
            model=response.model,
            prompt=context["message"],
            response=response.text,
            usage=response.usage
        )
        
        return {
            "text": response.text,
            "model": response.model,
            "usage": response.usage
        }
    
    def _select_model(self, preference: str) -> Optional[str]:
        """Выбор модели на основе предпочтений"""
        # Пока возвращаем None (автоматический выбор)
        # В будущем - логика выбора: local, cloud, cheap, strong
        return None
