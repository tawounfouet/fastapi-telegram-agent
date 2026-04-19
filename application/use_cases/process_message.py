from core.interfaces import BaseEngine, MessageRepository, ContextRepository
from core.schemas import MessageDTO, EngineResponseDTO

class ProcessMessageUseCase:
    """
    Cas d'usage principal : Traiter un message entrant.
    Cette classe orchestre la récupération du contexte, l'appel à l'Engine,
    et la sauvegarde de la réponse.
    """
    
    def __init__(
        self,
        engine: BaseEngine,
        message_repo: MessageRepository,
        context_repo: ContextRepository
    ):
        self.engine = engine
        self.message_repo = message_repo
        self.context_repo = context_repo

    async def execute(self, message: MessageDTO) -> EngineResponseDTO:
        user_id = message.user.id
        
        # 1. Récupérer le contexte utilisateur et l'historique
        context = await self.context_repo.get_context(user_id)
        history = await self.message_repo.get_history(user_id)
        context["history"] = history
        
        # 2. Appeler le moteur d'intelligence
        response = await self.engine.process(message, context)
        
        # 3. Mettre à jour et sauvegarder le contexte
        # (On retire l'historique avant de sauvegarder le contexte pur pour éviter la duplication)
        context.pop("history", None)
        await self.context_repo.save_context(user_id, context)
        
        # 4. Sauvegarder le message et la réponse
        await self.message_repo.save(message, response)
        
        return response
