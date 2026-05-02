import asyncio
import uuid
from typing import Optional
from .base import BaseInterface, InterfaceMessage


class CLIInterface(BaseInterface):
    """CLI интерфейс для взаимодействия с системой"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        super().__init__(name="cli", api_url=api_url)
        self.session_id = str(uuid.uuid4())
    
    async def start(self):
        """Запуск CLI интерфейса"""
        print("=" * 50)
        print("Local AI Agent - CLI Interface")
        print("=" * 50)
        print(f"Session ID: {self.session_id}")
        print("Type 'exit' or 'quit' to stop")
        print("Type 'new' to start a new session")
        print("=" * 50)
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'new':
                    self.session_id = str(uuid.uuid4())
                    print(f"New session started: {self.session_id}")
                    continue
                
                # Отправка сообщения
                message = InterfaceMessage(
                    session_id=self.session_id,
                    content=user_input,
                    input_type="text"
                )
                
                print("Assistant: ", end="", flush=True)
                response = await self.send_to_api(message)
                print(response.get("text", "Error: No response"))
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    async def stop(self):
        """Остановка CLI интерфейса"""
        pass
    
    def run(self):
        """Синхронный запуск"""
        asyncio.run(self.start())


if __name__ == "__main__":
    cli = CLIInterface()
    cli.run()
