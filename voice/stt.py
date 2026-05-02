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
    """STT используя локальный Whisper"""
    
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
    
    async def _load_model(self):
        """Ленивая загрузка модели"""
        if self._model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model: {self.model_name}")
                self._model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper model loaded successfully")
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
