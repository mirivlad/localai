from typing import List, Dict, Optional
from datetime import datetime, timedelta


class ShortTermMemory:
    """Кратковременная память (последние N сообщений)"""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict] = []
    
    def add_message(self, role: str, content: str, 
                    metadata: Optional[Dict] = None):
        """Добавление сообщения"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        # Ограничение размера
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_history(self, last_n: Optional[int] = None) -> List[Dict]:
        """Получение истории"""
        if last_n:
            return self.messages[-last_n:]
        return self.messages.copy()
    
    def get_context(self, max_tokens: int = 2000) -> List[Dict]:
        """Получение контекста с ограничением по токенам (приблизительно)"""
        context = []
        total_chars = 0
        
        # Идем с конца
        for msg in reversed(self.messages):
            msg_chars = len(msg['content']) + len(msg['role']) + 10
            if total_chars + msg_chars > max_tokens * 4:  # Примерно 4 символа = 1 токен
                break
            context.insert(0, msg)
            total_chars += msg_chars
        
        return context
    
    def clear(self):
        """Очистка памяти"""
        self.messages = []
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Простой поиск по содержимому"""
        results = []
        query_lower = query.lower()
        
        for msg in reversed(self.messages):
            if query_lower in msg['content'].lower():
                results.append(msg)
                if len(results) >= limit:
                    break
        
        return results
