from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class MessageORM(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    user_text: Mapped[str] = mapped_column(Text)
    bot_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    response_metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class UserContextORM(Base):
    __tablename__ = "user_contexts"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ── Module-level singletons ──────────────────────────────────────────────────

_engine = None
_session_factory = None


def get_engine(db_path: str):
    global _engine
    if _engine is None:
        url = f"sqlite+aiosqlite:///{db_path}"
        _engine = create_async_engine(url, echo=False)
    return _engine


def get_session_factory(db_path: str) -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        engine = get_engine(db_path)
        _session_factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def init_db(db_path: str) -> None:
    """Create parent directory and all tables if they don't exist yet."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine(db_path)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
