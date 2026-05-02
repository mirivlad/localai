from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class StateTracker:
    """Логирование состояний и действий системы"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.logs: List[Dict] = []
    
    def log_routing(self, session_id: str, message: str, router_output: Any):
        """Логирование решения роутера"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "routing",
            "session_id": session_id,
            "message": message[:100],  # Обрезаем для краткости
            "router_output": router_output.dict() if hasattr(router_output, 'dict') else str(router_output)
        }
        self._add_entry(entry)
    
    def log_model_call(self, session_id: str, provider: str, model: str, 
                       prompt: str, response: str, usage: Dict):
        """Логирование вызова модели"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "model_call",
            "session_id": session_id,
            "provider": provider,
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "usage": usage
        }
        self._add_entry(entry)
    
    def log_tool_usage(self, session_id: str, tool_name: str, 
                       action: str, result: Optional[str] = None):
        """Логирование использования инструментов"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "tool_usage",
            "session_id": session_id,
            "tool": tool_name,
            "action": action,
            "result_length": len(result) if result else 0
        }
        self._add_entry(entry)
    
    def log_agent_step(self, session_id: str, agent_name: str, 
                       step: int, action: str, thought: Optional[str] = None):
        """Логирование шага агента"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_step",
            "session_id": session_id,
            "agent": agent_name,
            "step": step,
            "action": action,
            "thought": thought[:200] if thought else None
        }
        self._add_entry(entry)
    
    def _add_entry(self, entry: Dict):
        """Добавление записи в лог"""
        self.logs.append(entry)
        
        # Запись в файл если указан
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            except Exception:
                pass  # Игнорируем ошибки записи лога
    
    def get_logs(self, session_id: Optional[str] = None, 
                 log_type: Optional[str] = None) -> List[Dict]:
        """Получение логов с фильтрацией"""
        filtered = self.logs
        
        if session_id:
            filtered = [l for l in filtered if l.get('session_id') == session_id]
        
        if log_type:
            filtered = [l for l in filtered if l.get('type') == log_type]
        
        return filtered
