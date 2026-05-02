from typing import Dict, List, Optional, Any
from datetime import datetime


class ContextBuilder:
    """Сбор контекста для субагентов"""
    
    def __init__(self, max_short_term: int = 10):
        self.max_short_term = max_short_term
        self.short_term_history: List[Dict] = []
    
    def build_context(self, session_id: str, message: str, 
                     router_output: Optional[Any] = None,
                     additional_context: Optional[Dict] = None) -> Dict:
        """Сборка контекста"""
        context = {
            "session_id": session_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "short_term_history": self._get_recent_history(),
        }
        
        if router_output:
            context["router"] = router_output.dict()
        
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def add_to_history(self, role: str, content: str):
        """Добавление сообщения в историю"""
        self.short_term_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничение размера истории
        if len(self.short_term_history) > self.max_short_term:
            self.short_term_history = self.short_term_history[-self.max_short_term:]
    
    def _get_recent_history(self) -> List[Dict]:
        """Получение последней истории"""
        return self.short_term_history[-self.max_short_term:]
    
    def clear_history(self):
        """Очистка истории"""
        self.short_term_history = []
