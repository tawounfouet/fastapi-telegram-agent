from telegram import Update
from core.schemas import MessageDTO, UserDTO
from application.use_cases.process_message import ProcessMessageUseCase
from delivery.formatters.telegram_formatter import TelegramFormatter
from datetime import datetime, timezone

class TelegramController:
    """
    Controller central pour Telegram.
    Reçoit un objet Update (que ce soit via polling ou webhook),
    le normalise en DTO métier, invoque le Use Case, puis retourne les réponses formatées.
    """
    
    def __init__(self, process_message_use_case: ProcessMessageUseCase):
        self.use_case = process_message_use_case

    async def handle_update(self, update: Update) -> list[str]:
        """
        Traite un Update Telegram et retourne une liste de messages texte à envoyer,
        ou une liste vide s'il n'y a rien à répondre.
        """
        if not update.message or not update.message.text:
            return []
            
        tg_user = update.message.from_user
        if not tg_user:
            return []

        # 1. Normalisation en DTO métier
        user_dto = UserDTO(
            id=str(tg_user.id),
            username=tg_user.username,
            is_bot=tg_user.is_bot
        )
        
        message_dto = MessageDTO(
            id=str(update.message.message_id),
            user=user_dto,
            text=update.message.text,
            timestamp=datetime.now(timezone.utc)
        )
        
        # 2. Exécution du Use Case principal
        response_dto = await self.use_case.execute(message_dto)
        
        # 3. Formatage pour Telegram (Delivery Layer)
        formatted_chunks = TelegramFormatter.format_response(response_dto)
        
        return formatted_chunks
