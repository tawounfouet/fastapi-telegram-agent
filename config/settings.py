import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "DEFAULT_TOKEN_FOR_TESTING"

    # Webhook
    WEBHOOK_URL: str = "https://example.com/webhook"

    # Engine configuration
    DEFAULT_ENGINE: str = "simple"  # options: simple, llm

    # LLM (Mock or OpenAI)
    OPENAI_API_KEY: str = ""

    # Database
    DB_PATH: str = "/app/data/bot.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
