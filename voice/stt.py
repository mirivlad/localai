import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import io

logger = logging.getLogger(__name__)


class BaseSTT(ABC):
    """Базовый класс для Speech-to-Text"""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Транскрибация аудио в текст"""
        pass
    
    @abstractmethod
    async def transcribe_file(self, file_path: str) -> str:
        """Транскрибация аудио файла"""
        pass


class WhisperSTT(BaseSTT):
    """STT используя локальный Whisper (с кэшированием модели)"""
    
    _model_cache = {}  # Кэш моделей {model_name: model}
    
    def __init__(self, model_name: str = None, device: str = "cpu", model_path: str = None):
        self.model_name = model_name or os.getenv("WHISPER_MODEL", "base")
        self.device = device
        self.model_path = model_path or os.getenv("WHISPER_MODEL_PATH", None)
        self._model = None
    
    async def _load_model(self):
        """Ленивая загрузка модели с кэшированием"""
        if self._model is None:
            try:
                import whisper
                
                # Кэш по пути или имени
                cache_key = self.model_path if self.model_path else self.model_name
                
                if cache_key in WhisperSTT._model_cache:
                    logger.info(f"Using cached Whisper model: {cache_key}")
                    self._model = WhisperSTT._model_cache[cache_key]
                    return
                
                # Загрузка
                if self.model_path and os.path.exists(self.model_path):
                    logger.info(f"Loading Whisper model from: {self.model_path}")
                    model = whisper.load_model(self.model_path, device=self.device)
                else:
                    logger.info(f"Loading Whisper model: {self.model_name}")
                    model = whisper.load_model(self.model_name, device=self.device)
                
                # Сохранение в кэш
                WhisperSTT._model_cache[cache_key] = model
                self._model = model
                
                logger.info("Whisper model loaded and cached successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Транскрибация аудио данных"""
        await self._load_model()
        
        try:
            # Сохранение во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            # Транскрибация
            result = self._model.transcribe(temp_path, language="ru")
            
            # Удаление временного файла
            import os
            os.unlink(temp_path)
            
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    async def transcribe_file(self, file_path: str) -> str:
        """Транскрибация аудио файла"""
        await self._load_model()
        
        try:
            result = self._model.transcribe(file_path, language="ru")
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""


class WhisperAPISTT(BaseSTT):
    """STT через OpenAI Whisper API (облачный)"""
    
    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Транскрибация аудио данных через API"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"
                )
            
            import os
            os.unlink(temp_path)
            
            return transcript.text.strip()
            
        except Exception as e:
            logger.error(f"API Transcription error: {e}")
            return ""
    
    async def transcribe_file(self, file_path: str) -> str:
        """Транскрибация файла через API"""
        try:
            with open(file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"
                )
            return transcript.text.strip()
        except Exception as e:
            logger.error(f"API Transcription error: {e}")
            return ""
