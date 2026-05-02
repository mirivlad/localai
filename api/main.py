from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List, Dict, Any
import asyncio
import time
import os
import sys
import base64

# Добавление корня проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ModelManager, ModelFactory, OpenAICompatibleProvider, ModelResponse
from config.loader import load_providers_config, get_fallback_chain
from orchestrator import Router, ContextBuilder, ExecutionManager, StateTracker
from loguru import logger

# Настройка логирования
logger.add("logs/app.log", rotation="10 MB", level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Local AI Agent",
    description="Локальная агентная платформа",
    version="0.1.0"
)

# Инициализация компонентов
model_manager = ModelManager()
execution_manager = None  # Будет инициализирован при старте


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global execution_manager
    
    # Создание .env если его нет
    env_file = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
    env_example = os.path.join(os.path.dirname(__file__), '..', 'config', '.env.example')
    if not os.path.exists(env_file) and os.path.exists(env_example):
        logger.info(f"Creating .env from example...")
        import shutil
        shutil.copy(env_example, env_file)
        logger.info(f"Created {env_file}. Please edit it with your API keys!")
    
    # Создание директорий если их нет
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'embeddings'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'whisper'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'piper'), exist_ok=True)
    
    # Загрузка провайдеров из конфигурации
    providers_config = load_providers_config(
        os.getenv('PROVIDERS_CONFIG', 'config/providers.yaml')
    )
    
    # Регистрация провайдеров через фабрику
    for config in providers_config:
        try:
            provider = ModelFactory.create_provider(config)
            model_manager.register_provider(provider)
        except Exception as e:
            logger.error(f"Failed to create provider {config.get('name', 'unknown')}: {e}")
    
    # Установка fallback цепочки
    fallback_chain = get_fallback_chain()
    model_manager.set_fallback_chain(fallback_chain)
    
    # Инициализация ExecutionManager
    execution_manager = ExecutionManager(model_manager)
    logger.info("System initialized successfully")


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
    """Основной endpoint для чата через оркестратор"""
    global execution_manager
    
    try:
        result = await execution_manager.execute(
            session_id=request.session_id,
            message=request.content
        )
        return ChatResponse(
            session_id=result["session_id"],
            text=result["text"],
            model=result["model"],
            usage=result["usage"]
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
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.content}
            ]
            
            # Получаем провайдера и делаем streaming запрос
            provider = None
            for p in model_manager.providers.values():
                if hasattr(p, 'client'):
                    provider = p
                    break
            
            if provider and hasattr(provider, 'client'):
                # OpenAI-compatible streaming
                stream = await provider.client.chat.completions.create(
                    model=request.model or provider.default_model,
                    messages=messages,
                    stream=True,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                # Fallback - обычный ответ
                result = await execution_manager.execute(
                    session_id=request.session_id,
                    message=request.content
                )
                yield result["text"]
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/voice")
async def voice_endpoint(session_id: str, audio_file: UploadFile = File(...)):
    """Обработка голосового сообщения через Voice Pipeline"""
    try:
        from voice.pipeline import VoicePipeline
        
        # Чтение аудио данных
        audio_data = await audio_file.read()
        
        # Создание pipeline и обработка
        pipeline = VoicePipeline(api_url=f"http://localhost:{os.getenv('API_PORT', '8000')}")
        result = await pipeline.process_voice(audio_data, session_id)
        
        if result["success"]:
            # Кодирование аудио в base64 для передачи
            audio_base64 = base64.b64encode(result["audio_response"]).decode('utf-8')
            
            return JSONResponse({
                "session_id": result["session_id"],
                "input_text": result["input_text"],
                "response_text": result["response_text"],
                "audio_base64": audio_base64,
                "model": result.get("model", "unknown"),
                "success": True
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.get("error", "Unknown error")
            }, status_code=500)
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/providers")
async def get_providers():
    """Получение списка провайдеров"""
    return {"providers": model_manager.get_provider_info()}
