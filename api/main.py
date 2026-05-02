from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List, Dict, Any
import asyncio
import time
import os

from models import ModelManager, OpenAICompatibleProvider, ModelResponse
from config.loader import load_providers_config, get_fallback_chain

app = FastAPI(
    title="Local AI Agent",
    description="Локальная агентная платформа",
    version="0.1.0"
)

# Инициализация ModelManager
model_manager = ModelManager()


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    # Загрузка провайдеров из конфигурации
    providers_config = load_providers_config(
        os.getenv('PROVIDERS_CONFIG', 'config/providers.yaml')
    )
    
    # Регистрация провайдеров
    for config in providers_config:
        provider = OpenAICompatibleProvider(config['name'], config)
        model_manager.register_provider(provider)
    
    # Установка fallback цепочки
    fallback_chain = get_fallback_chain()
    model_manager.set_fallback_chain(fallback_chain)


class ChatRequest(BaseModel):
    session_id: str
    input_type: str = "text"
    content: str
    metadata: Optional[dict] = {}
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    session_id: str
    text: str
    model: str = "unknown"
    usage: dict = {}


class Message(BaseModel):
    role: str
    content: str


class ChatMessagesRequest(BaseModel):
    session_id: str
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


@app.get("/")
async def root():
    return {
        "status": "ok", 
        "message": "Local AI Agent is running",
        "providers": model_manager.get_provider_info()
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной endpoint для чата"""
    try:
        response = await model_manager.generate(
            prompt=request.content,
            provider_name=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return ChatResponse(
            session_id=request.session_id,
            text=response.text,
            model=response.model,
            usage=response.usage
        )
    except Exception as e:
        return ChatResponse(
            session_id=request.session_id,
            text=f"Error: {str(e)}",
            model="error",
            usage={}
        )


@app.post("/chat/messages", response_model=ChatResponse)
async def chat_with_messages(request: ChatMessagesRequest):
    """Чат с историей сообщений"""
    try:
        messages = [msg.dict() for msg in request.messages]
        response = await model_manager.chat(
            messages=messages,
            provider_name=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return ChatResponse(
            session_id=request.session_id,
            text=response.text,
            model=response.model,
            usage=response.usage
        )
    except Exception as e:
        return ChatResponse(
            session_id=request.session_id,
            text=f"Error: {str(e)}",
            model="error",
            usage={}
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming endpoint для чата"""
    async def generate() -> AsyncGenerator[str, None]:
        # Заглушка - в будущем будет стриминг от модели
        words = f"Echo: {request.content}".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/voice")
async def voice():
    """Endpoint для голосовых сообщений"""
    # Заглушка
    return {"status": "not implemented"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/providers")
async def get_providers():
    """Получение списка провайдеров"""
    return {"providers": model_manager.get_provider_info()}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming endpoint для чата"""
    async def generate() -> AsyncGenerator[str, None]:
        # Заглушка - в будущем будет стриминг от модели
        words = f"Echo: {request.content}".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)
    
    return StreamingResponse(generate(), media_type="text/plain")
