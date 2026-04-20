import os
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

        @self.app.get("/", include_in_schema=False)
        async def homepage():
            from fastapi.responses import HTMLResponse
            version = os.getenv("APP_VERSION", "dev")
            env = os.getenv("ENVIRONMENT", "unknown")
            html = f"""<!DOCTYPE html>
                            <html lang="fr">
                            <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Telegram Bot API</title>
                            <style>
                                body {{ font-family: system-ui, sans-serif; max-width: 600px; margin: 80px auto; padding: 0 20px; color: #222; }}
                                h1 {{ font-size: 1.8rem; margin-bottom: 4px; }}
                                .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; margin-left: 8px; vertical-align: middle; }}
                                .badge-env {{ background: #e0f2fe; color: #0369a1; }}
                                .badge-ver {{ background: #dcfce7; color: #15803d; }}
                                p {{ color: #555; margin-top: 4px; }}
                                .links {{ margin-top: 32px; display: flex; gap: 12px; flex-wrap: wrap; }}
                                a.btn {{ display: inline-block; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.95rem; }}
                                .btn-primary {{ background: #2563eb; color: #fff; }}
                                .btn-secondary {{ background: #f1f5f9; color: #334155; }}
                                .status {{ margin-top: 40px; padding: 14px 18px; background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 4px; font-size: 0.9rem; }}
                            </style>
                            </head>
                            <body>
                            <h1>Telegram Bot API
                                <span class="badge badge-env">{env}</span>
                                <span class="badge badge-ver">v{version}</span>
                            </h1>
                            <p>Agent conversationnel Telegram propulsé par FastAPI.</p>

                            <div class="links">
                                <a class="btn btn-primary" href="/docs">Documentation Swagger</a>
                                <a class="btn btn-secondary" href="/redoc">ReDoc</a>
                                <a class="btn btn-secondary" href="/ping">Ping</a>
                                <a class="btn btn-secondary" href="/health">Health</a>
                            </div>

                            <div class="status">
                                ✅ Service opérationnel &mdash; <strong>POST /webhook</strong> prêt à recevoir les mises à jour Telegram.
                            </div>
                            </body>
                            </html>"""
            return HTMLResponse(content=html)

        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

        @self.app.get("/ping")
        async def ping():
            return {
                "status": "ok",
                "message": "pong",
                "version": os.getenv("APP_VERSION", "dev"),
                "env": os.getenv("ENVIRONMENT", "unknown"),
            }

    def get_app(self) -> FastAPI:
        return self.app
