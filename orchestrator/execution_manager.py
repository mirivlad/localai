import asyncio
from typing import Dict, Any, Optional, List
from .router import Router, RouterOutput
from .context_builder import ContextBuilder
from .state_tracker import StateTracker
from models import ModelManager
from agents.factory import AgentFactory
from agents.base import AgentResult
from memory import BehavioralMemory
from tools import ToolFactory


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
        self.tool_factory = ToolFactory()
        self.current_step = 0
    
    async def execute(self, session_id: str, message: str) -> Dict[str, Any]:
        """Выполнение запроса через оркестрацию с multi-step reasoning и timeout"""
        
        self.current_step = 0
        final_result = None
        
        try:
            # Выполнение с timeout
            final_result = await asyncio.wait_for(
                self._execution_loop(session_id, message),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            self.state_tracker.log_agent_step(
                session_id=session_id,
                agent_name="execution_manager",
                step=self.current_step,
                action="timeout",
                thought=f"Execution timeout after {self.timeout}s"
            )
            final_result = AgentResult(
                text=f"Timeout: execution exceeded {self.timeout} seconds",
                success=False,
                agent_name="execution_manager",
                tools_used=[]
            )
        
        return self._format_response(session_id, final_result)
    
    async def _execution_loop(self, session_id: str, original_message: str) -> AgentResult:
        """Основной цикл выполнения с multi-step reasoning"""
        
        message = original_message
        last_result = None
        
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            
            self.state_tracker.log_agent_step(
                session_id=session_id,
                agent_name="execution_manager",
                step=step,
                action="start_step",
                thought=f"Processing: {message[:50]}..."
            )
            
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
            
            # 4. Создание и выполнение субагента
            agent = self.agent_factory.create_agent(
                agent_type=router_output.subagent,
                model_manager=self.model_manager
            )
            
            self.state_tracker.log_agent_step(
                session_id=session_id,
                agent_name=agent.name,
                step=step,
                action="execute",
                thought=f"Intent: {router_output.intent}, Tools: {router_output.tools}, Model: {model_name}"
            )
            
            # Передаем выбранную модель в контекст
            context["selected_model"] = model_name
            agent_result = await agent.run(context)
            last_result = agent_result
            
            # 4. Выполнение инструментов если указаны в результате
            if agent_result.tools_used:
                tool_results = await self._execute_tools(
                    session_id, agent_result.tools_used, context
                )
                # Обновляем контекст с результатами инструментов
                context["tool_results"] = tool_results
            
            # 5. Проверка завершения
            if agent_result.success:
                # Сохранение/обновление в behavioral memory
                if step == 1:
                    # Новый паттерн
                    pattern_id = self.behavioral_memory.add_pattern(original_message, agent_result.text)
                    self.behavioral_memory.update_usage(pattern_id, success=True)
                else:
                    # Обновляем существующие паттерны
                    for pattern in self.behavioral_memory.search(original_message, limit=1):
                        if 'id' in pattern:
                            self.behavioral_memory.update_usage(pattern['id'], success=True)
                
                # Обновление истории
                self.context_builder.add_to_history("user", original_message)
                self.context_builder.add_to_history("assistant", agent_result.text)
                
                return agent_result
            
            else:
                # Обновление scoring при неудаче
                for pattern in self.behavioral_memory.search(original_message, limit=1):
                    if 'id' in pattern:
                        self.behavioral_memory.update_usage(pattern['id'], success=False)
            
            # Если не успешно и есть еще шаги, обновляем сообщение с анализом ошибки
            if step < self.max_steps:
                # Анализ причины ошибки для следующего шага
                error_analysis = f"Previous attempt failed: {agent_result.text}. "
                if agent_result.tools_used:
                    error_analysis += f"Tools used: {[t.get('name') for t in agent_result.tools_used]}. "
                error_analysis += "Please analyze the error and try a different approach."
                message = error_analysis
        
        # Если все шаги пройдены, возвращаем последний результат
        if last_result:
            self.state_tracker.log_agent_step(
                session_id=session_id,
                agent_name="execution_manager",
                step=self.max_steps,
                action="max_steps_reached",
                thought="Maximum steps reached without success"
            )
        
        return last_result or AgentResult(
            text="Failed to complete request within max steps",
            success=False,
            agent_name="execution_manager",
            tools_used=[]
        )
    
    async def _execute_tools(self, session_id: str, tools: List[Dict], 
                            context: Dict) -> List[Dict]:
        """Выполнение инструментов"""
        results = []
        
        for tool_info in tools:
            tool_name = tool_info.get("name")
            tool_action = tool_info.get("action", "execute")
            tool_params = tool_info.get("params", {})
            
            try:
                tool = self.tool_factory.create_tool(tool_name)
                
                self.state_tracker.log_tool_usage(
                    session_id=session_id,
                    tool_name=tool_name,
                    action=tool_action
                )
                
                result = await tool.execute(action=tool_action, **tool_params)
                
                results.append({
                    "tool": tool_name,
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                self.state_tracker.log_tool_usage(
                    session_id=session_id,
                    tool_name=tool_name,
                    action=tool_action,
                    result=f"Error: {str(e)}"
                )
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def _format_response(self, session_id: str, agent_result: AgentResult) -> Dict[str, Any]:
        """Форматирование финального ответа"""
        return {
            "session_id": session_id,
            "text": agent_result.text,
            "model": agent_result.metadata.get("model", "unknown") if agent_result.metadata else "unknown",
            "usage": agent_result.metadata.get("usage", {}) if agent_result.metadata else {},
            "agent": agent_result.agent_name,
            "tools_used": agent_result.tools_used,
            "success": agent_result.success,
            "steps_taken": self.current_step
        }
    
    def _select_model(self, preference: str) -> Optional[str]:
        """Выбор модели на основе предпочтений роутера"""
        # Мапинг предпочтений на конкретных провайдеров
        preference_map = {
            "local": "local_llm",
            "cloud": "openrouter",
            "cheap": "openrouter",
            "strong": "openai"
        }
        
        # Проверяем, доступен ли выбранный провайдер
        provider_name = preference_map.get(preference)
        if provider_name and self.model_manager.get_provider(provider_name):
            return provider_name
        
        # Fallback - возвращаем None (автоматический выбор)
        return None
