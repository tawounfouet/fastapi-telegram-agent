from abc import ABC, abstractmethod
from typing import List, Optional
from core.schemas import MessageDTO, EngineResponseDTO

class BaseEngine(ABC):
    """
    Interface abstraite pour tous les moteurs d'intelligence.
    Aucune dépendance à Telegram ici.
    """
    
    @abstractmethod
    async def process(self, message: MessageDTO, context: dict = None) -> EngineResponseDTO:
        """
        Traite un message utilisateur et retourne une réponse.
        """
        pass

class MessageRepository(ABC):
    """
    Interface pour sauvegarder l'historique des messages.
    """
    
    @abstractmethod
    async def save(self, message: MessageDTO, response: Optional[EngineResponseDTO] = None) -> None:
        pass
        
    @abstractmethod
    async def get_history(self, user_id: str, limit: int = 10) -> List[dict]:
        pass

class ContextRepository(ABC):
    """
    Interface pour gérer l'état de la conversation d'un utilisateur.
    """
    
    @abstractmethod
    async def get_context(self, user_id: str) -> dict:
        pass
        
    @abstractmethod
    async def save_context(self, user_id: str, context: dict) -> None:
        pass
