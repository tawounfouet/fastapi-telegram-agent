from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UserDTO(BaseModel):
    id: str
    username: Optional[str] = None
    is_bot: bool = False
    
class MessageDTO(BaseModel):
    id: str
    user: UserDTO
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class EngineResponseDTO(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
