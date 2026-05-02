import asyncio
import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .base import BaseInterface, InterfaceMessage

logger = logging.getLogger(__name__)


class TelegramInterface(BaseInterface):
    """Telegram бот интерфейс"""
    
    def __init__(self, token: str, api_url: str = "http://localhost:8000"):
        super().__init__(name="telegram", api_url=api_url)
        self.token = token
        self.application: Optional[Application] = None
        self.user_sessions: dict = {}  # user_id -> session_id
    
    async def start(self):
        """Запуск Telegram бота"""
        self.application = Application.builder().token(self.token).build()
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("new", self.new_session_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Telegram bot starting...")
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()
    
    async def stop(self):
        """Остановка Telegram бота"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = str(update.effective_user.id) + "_" + str(update.effective_message.date.timestamp())
        
        await update.message.reply_text(
            "Привет! Я локальный AI агент.\n"
            "Просто напиши мне сообщение, и я отвечу.\n"
            "Команды:\n"
            "/new - новая сессия\n"
            "/start - начать заново"
        )
    
    async def new_session_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /new - новая сессия"""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = str(user_id) + "_" + str(update.effective_message.date.timestamp())
        
        await update.message.reply_text("Новая сессия начата!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстового сообщения"""
        user_id = update.effective_user.id
        
        # Получение или создание сессии
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = str(user_id) + "_" + str(update.effective_message.date.timestamp())
        
        session_id = self.user_sessions[user_id]
        user_message = update.message.text
        
        # Отправка индикатора печати
        await update.message.chat.send_action(action="typing")
        
        try:
            # Отправка в API
            message = InterfaceMessage(
                session_id=session_id,
                content=user_message,
                input_type="text"
            )
            
            response = await self.send_to_api(message)
            text = response.get("text", "Извините, произошла ошибка.")
            
            await update.message.reply_text(text)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Произошла ошибка при обработке сообщения.")
