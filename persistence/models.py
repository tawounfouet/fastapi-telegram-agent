from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict

@dataclass
class MessageRecord:
    message_id: str
    user_id: str
    user_text: str
    bot_text: Optional[str]
    timestamp: datetime
    metadata: Dict

@dataclass
class UserContext:
    user_id: str
    state: Dict
    last_updated: datetime
