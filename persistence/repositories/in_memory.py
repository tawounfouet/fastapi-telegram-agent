from typing import List, Optional, Dict
from core.interfaces import MessageRepository, ContextRepository
from core.schemas import MessageDTO, EngineResponseDTO
from persistence.models import MessageRecord, UserContext
from datetime import datetime, timezone

class InMemoryMessageRepository(MessageRepository):
    def __init__(self):
        # user_id -> List[MessageRecord]
        self.storage: Dict[str, List[MessageRecord]] = {}
        
    async def save(self, message: MessageDTO, response: Optional[EngineResponseDTO] = None) -> None:
        user_id = message.user.id
        if user_id not in self.storage:
            self.storage[user_id] = []
            
        record = MessageRecord(
            message_id=message.id,
            user_id=user_id,
            user_text=message.text,
            bot_text=response.text if response else None,
            timestamp=message.timestamp,
            metadata=response.metadata if response else {}
        )
        self.storage[user_id].append(record)
        
    async def get_history(self, user_id: str, limit: int = 10) -> List[dict]:
        records = self.storage.get(user_id, [])
        return [{"user": r.user_text, "bot": r.bot_text} for r in records[-limit:]]


class InMemoryContextRepository(ContextRepository):
    def __init__(self):
        # user_id -> UserContext
        self.storage: Dict[str, UserContext] = {}
        
    async def get_context(self, user_id: str) -> dict:
        record = self.storage.get(user_id)
        if record:
            return record.state
        return {}
        
    async def save_context(self, user_id: str, context: dict) -> None:
        self.storage[user_id] = UserContext(
            user_id=user_id,
            state=context,
            last_updated=datetime.now(timezone.utc)
        )
