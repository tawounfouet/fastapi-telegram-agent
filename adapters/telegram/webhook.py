from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update, Bot
from adapters.telegram.controller import TelegramController


class TelegramWebhookAdapter:
    def __init__(self, token: str, controller: TelegramController):
        self.token = token
        self.bot = Bot(token=token)
        self.controller = controller
        self.app = FastAPI(title="Telegram Bot Webhook", lifespan=self._lifespan)
        self._setup_routes()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        # Initialise DB tables before accepting requests
        from persistence.database import init_db
        from config import settings
        await init_db(settings.DB_PATH)

        await self.bot.initialize()
        yield
        await self.bot.shutdown()

    def _setup_routes(self):
        @self.app.post("/webhook")
        async def handle_webhook(request: Request):
            data = await request.json()
            update = Update.de_json(data, self.bot)

            chunks = await self.controller.handle_update(update)

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
