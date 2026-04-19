import re
from core.schemas import EngineResponseDTO

class TelegramFormatter:
    """
    Formate la réponse de l'Engine pour qu'elle soit compatible avec Telegram.
    Gère l'échappement pour MarkdownV2 et le découpage des messages trop longs.
    """
    
    MAX_MESSAGE_LENGTH = 4000  # Limite Telegram : 4096 caractères
    
    @staticmethod
    def escape_markdown_v2(text: str) -> str:
        """
        Échappe les caractères spéciaux requis par Telegram MarkdownV2
        en dehors des blocs de code.
        (Version simplifiée pour l'exemple)
        """
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
        
    @classmethod
    def format_response(cls, response: EngineResponseDTO) -> list[str]:
        """
        Prend une réponse d'Engine, l'échappe et la découpe si nécessaire.
        Retourne une liste de chunks prêts à être envoyés.
        """
        formatted_text = cls.escape_markdown_v2(response.text)
        
        chunks = []
        for i in range(0, len(formatted_text), cls.MAX_MESSAGE_LENGTH):
            chunks.append(formatted_text[i:i + cls.MAX_MESSAGE_LENGTH])
            
        return chunks
