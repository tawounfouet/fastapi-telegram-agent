import sys
import uvicorn
from config import settings

# Persistence — SQLite (production) backed by the same interfaces as InMemory
from persistence.database import get_session_factory
from persistence.repositories.sqlite import SQLiteMessageRepository, SQLiteContextRepository

# Engines
from engines.registry import registry
from engines.simple.engine import SimpleEngine
from engines.llm.engine import LLMEngineMock

# Use Cases
from application.use_cases.process_message import ProcessMessageUseCase

# Adapters
from adapters.telegram.controller import TelegramController
from adapters.telegram.polling import TelegramPollingAdapter
from adapters.telegram.webhook import TelegramWebhookAdapter


def bootstrap() -> TelegramController:
    """
    Injection de dépendances et assemblage de l'architecture.
    La session factory SQLAlchemy est créée ici ; init_db() est appelé
    depuis le lifespan FastAPI (mode webhook) ou juste avant run_polling().
    """
    session_factory = get_session_factory(settings.DB_PATH)

    message_repo = SQLiteMessageRepository(session_factory)
    context_repo = SQLiteContextRepository(session_factory)

    simple_engine = SimpleEngine()
    llm_engine = LLMEngineMock()
    registry.register("simple", simple_engine)
    registry.register("llm", llm_engine)

    active_engine = registry.get_engine(settings.DEFAULT_ENGINE)

    process_message_use_case = ProcessMessageUseCase(
        engine=active_engine,
        message_repo=message_repo,
        context_repo=context_repo,
    )

    return TelegramController(process_message_use_case)


def run_polling(controller: TelegramController) -> None:
    import asyncio
    from persistence.database import init_db

    asyncio.run(init_db(settings.DB_PATH))
    adapter = TelegramPollingAdapter(token=settings.TELEGRAM_BOT_TOKEN, controller=controller)
    adapter.run()


def run_webhook(controller: TelegramController) -> None:
    # DB init happens inside the FastAPI lifespan (see webhook.py)
    adapter = TelegramWebhookAdapter(token=settings.TELEGRAM_BOT_TOKEN, controller=controller)
    app = adapter.get_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    controller = bootstrap()

    mode = sys.argv[1] if len(sys.argv) > 1 else "polling"

    if mode == "webhook":
        run_webhook(controller)
    else:
        run_polling(controller)
