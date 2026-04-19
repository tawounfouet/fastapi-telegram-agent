import sys
import uvicorn
from config import settings

# Persistance
from persistence.repositories.in_memory import InMemoryMessageRepository, InMemoryContextRepository

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

def bootstrap():
    """
    Injection de dépendances manuelle et assemblage de l'architecture.
    """
    
    # 1. Instancier la persistance
    message_repo = InMemoryMessageRepository()
    context_repo = InMemoryContextRepository()
    
    # 2. Instancier et enregistrer les engines
    simple_engine = SimpleEngine()
    llm_engine = LLMEngineMock()
    
    registry.register("simple", simple_engine)
    registry.register("llm", llm_engine)
    
    # Choisir l'engine actif
    active_engine = registry.get_engine(settings.DEFAULT_ENGINE)
    
    # 3. Instancier le Use Case principal
    process_message_use_case = ProcessMessageUseCase(
        engine=active_engine,
        message_repo=message_repo,
        context_repo=context_repo
    )
    
    # 4. Instancier le controller Telegram
    telegram_controller = TelegramController(process_message_use_case)
    
    return telegram_controller

def run_polling(controller: TelegramController):
    adapter = TelegramPollingAdapter(
        token=settings.TELEGRAM_BOT_TOKEN,
        controller=controller
    )
    adapter.run()

def run_webhook(controller: TelegramController):
    adapter = TelegramWebhookAdapter(
        token=settings.TELEGRAM_BOT_TOKEN,
        controller=controller
    )
    app = adapter.get_app()
    # Démarrage de uvicorn (le port peut être configuré)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    controller = bootstrap()
    
    mode = "polling"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
    if mode == "webhook":
        run_webhook(controller)
    else:
        run_polling(controller)
