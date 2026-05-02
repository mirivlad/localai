import logging
from typing import Optional, Dict, Any
from .stt import BaseSTT, WhisperSTT
from .tts import BaseTTS, PiperTTS

logger = logging.getLogger(__name__)


class VoicePipeline:
    """Полный пайплайн: аудио → текст → обработка → текст → аудио"""
    
    def __init__(self, stt: Optional[BaseSTT] = None, 
                 tts: Optional[BaseTTS] = None,
                 api_url: str = "http://localhost:8000"):
        self.stt = stt or WhisperSTT()
        self.tts = tts or PiperTTS()
        self.api_url = api_url
    
    async def process_voice(self, audio_data: bytes, 
                           session_id: str) -> Dict[str, Any]:
        """Полная обработка голосового сообщения"""
        
        # 1. STT: аудио → текст
        logger.info("Starting STT transcription...")
        text = await self.stt.transcribe(audio_data)
        
        if not text:
            return {
                "success": False,
                "error": "Failed to transcribe audio",
                "text": "",
                "audio_response": None
            }
        
        logger.info(f"Transcribed: {text[:50]}...")
        
        # 2. Отправка в API (оркестратор)
        logger.info("Sending to orchestrator...")
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/chat",
                json={
                    "session_id": session_id,
                    "input_type": "voice",
                    "content": text,
                    "metadata": {"source": "voice"}
                }
            )
            result = response.json()
        
        response_text = result.get("text", "")
        logger.info(f"Response: {response_text[:50]}...")
        
        # 3. TTS: текст → аудио
        logger.info("Starting TTS synthesis...")
        audio_response = await self.tts.synthesize(response_text)
        
        return {
            "success": True,
            "input_text": text,
            "response_text": response_text,
            "audio_response": audio_response,
            "session_id": session_id,
            "model": result.get("model", "unknown")
        }
    
    async def transcribe_only(self, audio_data: bytes) -> str:
        """Только транскрибация (без отправки в API)"""
        return await self.stt.transcribe(audio_data)
    
    async def synthesize_only(self, text: str) -> bytes:
        """Только синтез речи (без STT)"""
        return await self.tts.synthesize(text)
