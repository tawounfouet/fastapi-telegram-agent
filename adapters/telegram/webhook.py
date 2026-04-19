from fastapi import FastAPI, Request
from telegram import Update, Bot
from adapters.telegram.controller import TelegramController

class TelegramWebhookAdapter:
    def __init__(self, token: str, controller: TelegramController):
        self.token = token
        self.bot = Bot(token=token)
        self.controller = controller
        self.app = FastAPI(title="Telegram Bot Webhook")
        self._setup_routes()
        
    def _setup_routes(self):
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.bot.initialize()
            yield
            await self.bot.shutdown()

        self.app.router.lifespan_context = lifespan

        @self.app.post("/webhook")
        async def handle_webhook(request: Request):
            data = await request.json()
            update = Update.de_json(data, self.bot)
            
            # Traiter via le controller
            chunks = await self.controller.handle_update(update)
            
            # Envoyer les réponses directement via l'instance du bot
            if update.message and chunks:
                chat_id = update.message.chat_id
                for chunk in chunks:
                    await self.bot.send_message(chat_id=chat_id, text=chunk)
                    
            return {"status": "ok"}
            
        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

    def get_app(self) -> FastAPI:
        return self.app
