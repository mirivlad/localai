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
        """HTML страница для чата"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Local AI Agent - Web UI</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; }
        .message { margin: 10px 0; padding: 5px; }
        .user { background: #e3f2fd; }
        .assistant { background: #f5f5f5; }
        input { width: 80%; padding: 5px; }
        button { padding: 5px 15px; }
    </style>
</head>
<body>
    <h1>Local AI Agent - Web Interface</h1>
    <div id="chat"></div>
    <input type="text" id="messageInput" placeholder="Type a message..." />
    <button onclick="sendMessage()">Send</button>
    
    <script>
        const ws = new WebSocket("ws://" + window.location.host + "/ws");
        const chat = document.getElementById("chat");
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === "response") {
                addMessage("Assistant: " + data.text, "assistant");
            }
        };
        
        function sendMessage() {
            const input = document.getElementById("messageInput");
            const message = input.value;
            if (message) {
                addMessage("You: " + message, "user");
                ws.send(JSON.stringify({message: message}));
                input.value = "";
            }
        }
        
        function addMessage(text, className) {
            const div = document.createElement("div");
            div.className = "message " + className;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        document.getElementById("messageInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });
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
