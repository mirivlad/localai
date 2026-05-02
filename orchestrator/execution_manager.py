from typing import Dict, Any, Optional, List
from .router import Router, RouterOutput
from .context_builder import ContextBuilder
from .state_tracker import StateTracker
from models import ModelManager
from agents.factory import AgentFactory
from memory import BehavioralMemory


class ExecutionManager:
    """Управление выполнением запросов с multi-step reasoning"""
    
    def __init__(self, model_manager: ModelManager, 
                 max_steps: int = 5, timeout: int = 60):
        self.model_manager = model_manager
        self.max_steps = max_steps
        self.timeout = timeout
        self.router = Router(model_manager)
        self.context_builder = ContextBuilder()
        self.state_tracker = StateTracker()
        self.agent_factory = AgentFactory()
        self.behavioral_memory = BehavioralMemory()
        self.current_step = 0
    
    async def execute(self, session_id: str, message: str) -> Dict[str, Any]:
        """Выполнение запроса через оркестрацию с multi-step reasoning"""
        
        self.current_step = 0
        final_result = None
        
        # Проверка в behavioral memory
        behavioral_results = self.behavioral_memory.search(message, limit=1)
        if behavioral_results and behavioral_results[0]['final_score'] > 0.8:
            # Используем сохраненный паттерн
            return {
                "session_id": session_id,
                "text": behavioral_results[0]['response'],
                "model": "behavioral_memory",
                "usage": {},
                "router": {"intent": "chat", "subagent": "chat", "confidence": behavioral_results[0]['final_score']},
                "agent": "behavioral",
                "tools_used": [],
                "success": True,
                "from_cache": True
            }
        
        # Основной цикл выполнения
        while self.current_step < self.max_steps:
            self.current_step += 1
            
            # 1. Роутинг
            router_output: RouterOutput = await self.router.route(message)
            self.state_tracker.log_routing(session_id, message, router_output)
            
            # 2. Сбор контекста
            context = self.context_builder.build_context(
                session_id=session_id,
                message=message,
                router_output=router_output
            )
            
            # 3. Выбор модели
            model_name = self._select_model(router_output.model_preference)
            
            # 4. Создание и выполнение субагента
            agent = self.agent_factory.create_agent(
                agent_type=router_output.subagent,
                model_manager=self.model_manager
            )
            
            self.state_tracker.log_agent_step(
                session_id=session_id,
                agent_name=agent.name,
                step=self.current_step,
                action="execute",
                thought=f"Intent: {router_output.intent}"
            )
            
            agent_result = await agent.run(context)
            
            # 5. Проверка завершения
            if agent_result.success or self.current_step >= self.max_steps:
                final_result = agent_result
                break
            
            # Если не успешно, пробуем снова с обновленным контекстом
            message = f"Previous attempt failed: {agent_result.text}. Please try again."
        
        if not final_result:
            final_result = agent_result  # Возвращаем последний результат
        
        # 6. Обновление истории
        self.context_builder.add_to_history("user", message)
        self.context_builder.add_to_history("assistant", final_result.text)
        
        # 7. Сохранение в behavioral memory если успешно
        if final_result.success:
            self.behavioral_memory.add_pattern(message, final_result.text)
        
        return {
            "session_id": session_id,
            "text": final_result.text,
            "model": "unknown",
            "usage": {},
            "router": router_output.dict() if 'router_output' in locals() else {},
            "agent": final_result.agent_name,
            "tools_used": final_result.tools_used,
            "success": final_result.success,
            "steps_taken": self.current_step
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
