from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import asyncio
import time

app = FastAPI(
    title="Local AI Agent",
    description="Локальная агентная платформа",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    session_id: str
    input_type: str = "text"
    content: str
    metadata: Optional[dict] = {}


class ChatResponse(BaseModel):
    session_id: str
    text: str
    model: str = "unknown"
    usage: dict = {}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Local AI Agent is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной endpoint для чата"""
    # Заглушка - в будущем будет вызов orchestrator
    return ChatResponse(
        session_id=request.session_id,
        text=f"Echo: {request.content}",
        model="echo",
        usage={"prompt_tokens": 0, "completion_tokens": 0}
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
