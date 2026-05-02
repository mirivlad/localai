from typing import List, Dict, Any, Optional
import os
import numpy as np


class VectorMemory:
    """Долговременная память на основе FAISS"""
    
    def __init__(self, index_path: str = None,
                 embedding_model: str = None,
                 embedding_model_path: str = None):
        # Пути по умолчанию из переменных окружения или дефолтные
        self.index_path = index_path or os.getenv("VECTOR_INDEX_PATH", "./data/faiss_index")
        self.embedding_model_name = embedding_model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedding_model_path = embedding_model_path or os.getenv("EMBEDDING_MODEL_PATH", None)
        self.embedding_model = None
        self.index = None
        self.documents: List[Dict] = []
        self._initialize()
    
    def _initialize(self):
        """Инициализация FAISS и модели эмбеддингов"""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Если указан путь к модели - загружаем оттуда, иначе по имени
            if self.embedding_model_path and os.path.exists(self.embedding_model_path):
                print(f"Loading embedding model from: {self.embedding_model_path}")
                self.embedding_model = SentenceTransformer(self.embedding_model_path)
            else:
                print(f"Loading embedding model: {self.embedding_model_name}")
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                doc_path = self.index_path + ".docs"
                if os.path.exists(doc_path):
                    import pickle
                    with open(doc_path, 'rb') as f:
                        self.documents = pickle.load(f)
            else:
                dimension = self.embedding_model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatL2(dimension)
        
        except ImportError as e:
            raise Exception(f"Missing dependencies: {e}")
    
    def add_document(self, content: str, metadata: Optional[Dict] = None) -> int:
        """Добавление документа в память"""
        if not self.embedding_model or not self.index:
            raise Exception("Vector memory not initialized")
        
        embedding = self.embedding_model.encode([content])[0]
        self.index.add(np.array([embedding], dtype=np.float32))
        
        from datetime import datetime
        doc_id = len(self.documents)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        
        # Сохранение отключено (будет batch save)
        # self._save()
        return doc_id
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Поиск релевантных документов"""
        if not self.embedding_model or not self.index:
            raise Exception("Vector memory not initialized")
        
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.embedding_model.encode([query])[0]
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32), 
            min(k, self.index.ntotal)
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(distances[0][i])
                results.append(doc)
        
        return results
    
    def _save(self):
        """Сохранение индекса и документов"""
        if self.index:
            import faiss
            faiss.write_index(self.index, self.index_path)
            
            doc_path = self.index_path + ".docs"
            import pickle
            with open(doc_path, 'wb') as f:
                pickle.dump(self.documents, f)
    
    def save(self):
        """Явное сохранение (batch save)"""
        self._save()
    
    def clear(self):
        """Очистка памяти"""
        if self.index:
            self.index.reset()
        self.documents = []
        self._save()
