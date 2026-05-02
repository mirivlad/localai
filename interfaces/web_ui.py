from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import uuid
import json
from .base import BaseInterface, InterfaceMessage


class WebUIInterface(BaseInterface):
    """Web UI интерфейс для дебаггинга и управления"""
    
    def __init__(self, api_url: str = "http://localhost:8000", port: int = 8080):
        super().__init__(name="web_ui", api_url=api_url)
        self.port = port
        self.app = FastAPI(title="Local AI Agent - Web UI")
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, str] = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """Настройка маршрутов"""
        
        @self.app.get("/")
        async def get():
            return HTMLResponse(self._get_html())
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            session_id = str(uuid.uuid4())
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Отправка индикатора печати
                    await websocket.send_json({
                        "type": "typing",
                        "status": True
                    })
                    
                    # Отправка в API
                    message = InterfaceMessage(
                        session_id=session_id,
                        content=message_data.get("message", ""),
                        input_type="text"
                    )
                    
                    response = await self.send_to_api(message)
                    
                    # Отправка ответа
                    await websocket.send_json({
                        "type": "response",
                        "text": response.get("text", ""),
                        "session_id": session_id,
                        "model": response.get("model", "unknown")
                    })
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
        
        @self.app.get("/api/sessions")
        async def get_sessions():
            return {"sessions": list(self.user_sessions.keys())}
    
    def _get_html(self) -> str:
        """HTML страница для чата с поддержкой голоса"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Local AI Agent - Web UI</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin:0; padding:0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
               background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #10a37f; color: white; padding: 15px 20px; 
                   display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.2em; }
        .header .status { font-size: 0.9em; opacity: 0.9; }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; 
                          display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 70%; padding: 12px 16px; border-radius: 18px; 
                    line-height: 1.4; word-wrap: break-word; }
        .user-message { align-self: flex-end; background: #10a37f; color: white; 
                        border-bottom-right-radius: 5px; }
        .assistant-message { align-self: flex-start; background: white; color: #1a1a1a; 
                              border-bottom-left-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .typing-indicator { align-self: flex-start; background: white; 
                           padding: 12px 16px; border-radius: 18px; 
                           border-bottom-left-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .typing-indicator span { display: inline-block; width: 8px; height: 8px; 
                          background: #999; border-radius: 50%; margin: 0 2px; 
                          animation: typing 1.4s infinite; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 60%, 100% { transform: translateY(0); } 
                               30% { transform: translateY(-10px); } }
        .input-container { padding: 20px; background: white; 
                          border-top: 1px solid #e0e0e0; display: flex; gap: 10px; }
        .input-container input { flex: 1; padding: 12px 16px; border: 1px solid #e0e0e0; 
                                 border-radius: 25px; outline: none; font-size: 1em; }
        .input-container input:focus { border-color: #10a37f; }
        .input-container button { padding: 12px 24px; background: #10a37f; color: white; 
                                  border: none; border-radius: 25px; cursor: pointer; 
                                  font-size: 1em; transition: background 0.3s; }
        .input-container button:hover { background: #0d8c6a; }
        .input-container button:disabled { background: #ccc; cursor: not-allowed; }
        .voice-btn { background: #ff4081 !important; }
        .voice-btn:hover { background: #e91e63 !important; }
        .voice-btn.recording { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); }
                            50% { transform: scale(1.1); } }
        .model-info { font-size: 0.8em; color: #666; text-align: center; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Local AI Agent</h1>
        <div class="status" id="status">Подключение...</div>
    </div>
    
    <div class="chat-container" id="chat"></div>
    
    <div class="model-info" id="model-info"></div>
    
    <div class="input-container">
        <input type="text" id="messageInput" placeholder="Введите сообщение..." autocomplete="off" />
        <button onclick="toggleVoice()" id="voiceButton" class="voice-btn">🎤</button>
        <button onclick="sendMessage()" id="sendButton">Отправить</button>
    </div>
    
    <script>
        const ws = new WebSocket("ws://" + window.location.host + "/ws");
        const chat = document.getElementById("chat");
        const status = document.getElementById("status");
        const modelInfo = document.getElementById("model-info");
        const input = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");
        const voiceButton = document.getElementById("voiceButton");
        let isTyping = false;
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;
        
        ws.onopen = function() {
            status.textContent = "Подключено";
            status.style.opacity = "1";
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === "typing") {
                if (data.status) {
                    showTypingIndicator();
                } else {
                    removeTypingIndicator();
                }
            } else if (data.type === "response") {
                removeTypingIndicator();
                addMessage("Assistant: " + data.text, "assistant-message");
                if (data.model) {
                    modelInfo.textContent = "Model: " + data.model;
                }
            } else if (data.type === "audio_response") {
                // Воспроизведение аудио ответа
                const audio = new Audio("data:audio/wav;base64," + data.audio_base64);
                audio.play();
            }
        };
        
        ws.onclose = function() {
            status.textContent = "Отключено";
            status.style.opacity = "0.7";
        };
        
        function sendMessage() {
            const message = input.value.trim();
            if (!message || isTyping) return;
            
            addMessage("Вы: " + message, "user-message");
            ws.send(JSON.stringify({message: message}));
            input.value = "";
            input.focus();
        }
        
        async function toggleVoice() {
            if (!isRecording) {
                // Начать запись
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64Audio = reader.result.split(',')[1];
                            ws.send(JSON.stringify({ 
                                type: 'voice', 
                                audio: base64Audio 
                            }));
                        };
                        reader.readAsDataURL(audioBlob);
                        stream.getTracks().forEach(track => track.stop());
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    voiceButton.classList.add('recording');
                    voiceButton.textContent = '⏹️';
                } catch (err) {
                    alert('Ошибка доступа к микрофону: ' + err.message);
                }
            } else {
                // Остановить запись
                mediaRecorder.stop();
                isRecording = false;
                voiceButton.classList.remove('recording');
                voiceButton.textContent = '🎤';
            }
        }
        
        function addMessage(text, className) {
            const div = document.createElement("div");
            div.className = "message " + className;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function showTypingIndicator() {
            if (document.getElementById("typing")) return;
            isTyping = true;
            sendButton.disabled = true;
            voiceButton.disabled = true;
            const div = document.createElement("div");
            div.className = "typing-indicator";
            div.id = "typing";
            div.innerHTML = "<span></span><span></span><span></span>";
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function removeTypingIndicator() {
            const typing = document.getElementById("typing");
            if (typing) typing.remove();
            isTyping = false;
            sendButton.disabled = false;
            voiceButton.disabled = false;
        }
        
        input.addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });
        
        // Автофокус
        input.focus();
    </script>
</body>
</html>
        """
    
    async def start(self):
        """Запуск Web UI (должен запускаться через uvicorn)"""
        import uvicorn
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port)
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Остановка Web UI"""
        pass
