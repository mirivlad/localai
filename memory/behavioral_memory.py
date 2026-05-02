from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class BehavioralMemory:
    """Поведенческая память с системой скоринга"""
    
    def __init__(self, storage_path: str = "./data/behavioral.json"):
        self.storage_path = storage_path
        self.patterns: List[Dict] = []
        self._load()
    
    def add_pattern(self, pattern: str, response: str, 
                    metadata: Optional[Dict] = None) -> int:
        """Добавление патерна поведения"""
        pattern_id = len(self.patterns)
        
        self.patterns.append({
            "id": pattern_id,
            "pattern": pattern,
            "response": response,
            "score": 1.0,  # Начальный скор
            "usage_count": 0,
            "last_used": None,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        self._save()
        return pattern_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Поиск релевантных паттернов с учетом скоринга"""
        results = []
        
        for pattern in self.patterns:
            # Простая проверка вхождения (в будущем - векторный поиск)
            similarity = self._calculate_similarity(query, pattern['pattern'])
            
            if similarity > 0:
                # Итоговый скор: similarity * 0.7 + score * 0.3
                final_score = similarity * 0.7 + pattern['score'] * 0.3
                
                results.append({
                    **pattern,
                    "similarity": similarity,
                    "final_score": final_score
                })
        
        # Сортировка по final_score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return results[:limit]
    
    def update_usage(self, pattern_id: int, success: bool = True):
        """Обновление использования паттерна"""
        if pattern_id < len(self.patterns):
            pattern = self.patterns[pattern_id]
            pattern['usage_count'] += 1
            pattern['last_used'] = datetime.now().isoformat()
            
            # Обновление скора на основе успешности
            if success:
                pattern['score'] = min(10.0, pattern['score'] + 0.1)
            else:
                pattern['score'] = max(0.0, pattern['score'] - 0.2)
            
            self._save()
    
    def _calculate_similarity(self, query: str, pattern: str) -> float:
        """Расчет схожести (упрощенный)"""
        query_words = set(query.lower().split())
        pattern_words = set(pattern.lower().split())
        
        if not query_words or not pattern_words:
            return 0.0
        
        intersection = query_words.intersection(pattern_words)
        union = query_words.union(pattern_words)
        
        jaccard = len(intersection) / len(union) if union else 0.0
        return jaccard
    
    def _load(self):
        """Загрузка из файла"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.patterns = []
    
    def _save(self):
        """Сохранение в файл"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)
    
    def clear(self):
        """Очистка памяти"""
        self.patterns = []
        self._save()
