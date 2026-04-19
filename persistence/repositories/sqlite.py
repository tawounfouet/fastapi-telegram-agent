from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.interfaces import MessageRepository, ContextRepository
from core.schemas import MessageDTO, EngineResponseDTO
from persistence.database import MessageORM, UserContextORM


class SQLiteMessageRepository(MessageRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, message: MessageDTO, response: Optional[EngineResponseDTO] = None) -> None:
        async with self.session_factory() as session:
            record = MessageORM(
                message_id=message.id,
                user_id=message.user.id,
                user_text=message.text,
                bot_text=response.text if response else None,
                timestamp=message.timestamp,
                response_metadata=response.metadata if response else {},
            )
            session.add(record)
            await session.commit()

    async def get_history(self, user_id: str, limit: int = 10) -> List[dict]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(MessageORM)
                .where(MessageORM.user_id == user_id)
                .order_by(MessageORM.timestamp.desc())
                .limit(limit)
            )
            records = result.scalars().all()
            return [
                {"user": r.user_text, "bot": r.bot_text}
                for r in reversed(records)
            ]


class SQLiteContextRepository(ContextRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_context(self, user_id: str) -> dict:
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserContextORM).where(UserContextORM.user_id == user_id)
            )
            record = result.scalar_one_or_none()
            return record.state if record else {}

    async def save_context(self, user_id: str, context: dict) -> None:
        async with self.session_factory() as session:
            # Upsert: insert or replace
            stmt = sqlite_insert(UserContextORM).values(
                user_id=user_id,
                state=context,
                last_updated=datetime.now(timezone.utc),
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_id"],
                set_={"state": context, "last_updated": datetime.now(timezone.utc)},
            )
            await session.execute(stmt)
            await session.commit()
