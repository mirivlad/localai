import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import io

logger = logging.getLogger(__name__)


class BaseTTS(ABC):
    """Базовый класс для Text-to-Speech"""
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Синтез речи из текста, возвращает аудио данные"""
        pass
    
    @abstractmethod
    async def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """Синтез речи в файл"""
        pass


class PiperTTS(BaseTTS):
    """TTS используя Piper (локальный, быстрый)"""
    
    def __init__(self, model_path: Optional[str] = None, 
                 piper_executable: str = "piper"):
        self.model_path = model_path
        self.piper_executable = piper_executable
        self._check_available()
    
    def _check_available(self):
        """Проверка доступности Piper"""
        import subprocess
        try:
            subprocess.run([self.piper_executable, "--help"], 
                          capture_output=True, check=True)
            logger.info("Piper TTS is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Piper TTS not found. Install: pip install piper-tts")
            raise
    
    async def synthesize(self, text: str) -> bytes:
        """Синтез речи через Piper"""
        import subprocess
        import tempfile
        
        try:
            # Создание временных файлов
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                text_file = f.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                output_file = f.name
            
            # Команда Piper
            cmd = [self.piper_executable]
            if self.model_path:
                cmd.extend(["--model", self.model_path])
            cmd.extend(["--output_file", output_file])
            
            # Запуск
            with open(text_file, 'r') as stdin_file:
                subprocess.run(cmd, stdin=stdin_file, capture_output=True, check=True)
            
            # Чтение результата
            with open(output_file, 'rb') as f:
                audio_data = f.read()
            
            # Удаление временных файлов
            import os
            os.unlink(text_file)
            os.unlink(output_file)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Piper TTS error: {e}")
            return b""
    
    async def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """Синтез речи в файл"""
        try:
            audio_data = await self.synthesize(text)
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            return True
        except Exception as e:
            logger.error(f"Piper TTS file error: {e}")
            return False


class CoquiTTS(BaseTTS):
    """TTS используя Coqui TTS (локальный)"""
    
    def __init__(self, model_name: str = "tts_models/ru/tacotron2-DDC"):
        self.model_name = model_name
        self._model = None
    
    async def _load_model(self):
        """Ленивая загрузка модели"""
        if self._model is None:
            try:
                from TTS.api import TTS
                logger.info(f"Loading Coqui TTS model: {self.model_name}")
                self._model = TTS(model_name=self.model_name)
                logger.info("Coqui TTS model loaded")
            except Exception as e:
                logger.error(f"Failed to load Coqui TTS: {e}")
                raise
    
    async def synthesize(self, text: str) -> bytes:
        """Синтез речи через Coqui TTS"""
        await self._load_model()
        
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
            
            self._model.tts_to_file(text=text, file_path=temp_path)
            
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            import os
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Coqui TTS error: {e}")
            return b""
    
    async def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """Синтез речи в файл"""
        try:
            await self._load_model()
            self._model.tts_to_file(text=text, file_path=output_path)
            return True
        except Exception as e:
            logger.error(f"Coqui TTS file error: {e}")
            return False
