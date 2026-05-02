from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel


class InterfaceMessage(BaseModel):
    """Сообщение от интерфейса"""
    session_id: str
    content: str
    input_type: str = "text"  # text, voice
    metadata: Dict[str, Any] = {}


class BaseInterface(ABC):
    """Базовый класс для всех интерфейсов"""
    
    def __init__(self, name: str, api_url: str = "http://localhost:8000"):
        self.name = name
        self.api_url = api_url
    
    @abstractmethod
    async def start(self):
        """Запуск интерфейса"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Остановка интерфейса"""
        pass
    
    async def send_to_api(self, message: InterfaceMessage) -> Dict[str, Any]:
        """Отправка сообщения в API"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            # Определение endpoint в зависимости от типа сообщения
            if message.input_type == "voice" and message.metadata.get("audio_base64"):
                # Голосовое сообщение
                files = {
                    'audio_file': ('voice.wav', message.metadata["audio_base64"], 'audio/wav')
                }
                data = {'session_id': message.session_id}
                response = await client.post(
                    f"{self.api_url}/voice",
                    files=files,
                    data=data
                )
            else:
                # Текстовое сообщение
                response = await client.post(
                    f"{self.api_url}/chat",
                    json={
                        "session_id": message.session_id,
                        "input_type": message.input_type,
                        "content": message.content,
                        "metadata": message.metadata
                    }
                )
            return response.json()
    
    async def send_to_api_stream(self, message: InterfaceMessage) -> AsyncGenerator[str, None]:
        """Стриминговая отправка в API"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.api_url}/chat/stream",
                json={
                    "session_id": message.session_id,
                    "input_type": message.input_type,
                    "content": message.content,
                    "metadata": message.metadata
                }
            ) as response:
                async for chunk in response.aiter_text():
                    yield chunk
