from openai import AsyncOpenAI
from core.interfaces import BaseEngine
from core.schemas import MessageDTO, EngineResponseDTO
from config import settings


class LLMEngineMock(BaseEngine):
    """
    Moteur LLM reel base sur OpenAI (GPT-4o-mini).
    """

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def process(self, message: MessageDTO, context: dict = None) -> EngineResponseDTO:
        messages = []

        history = context.get("history", []) if context else []
        for entry in history[-10:]:
            messages.append({"role": "user", "content": entry.get("user", "")})
            messages.append({"role": "assistant", "content": entry.get("assistant", "")})

        messages.append({"role": "user", "content": message.text})

        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        reply = response.choices[0].message.content
        tokens = response.usage.total_tokens

        if context is not None:
            history.append({"user": message.text, "assistant": reply})
            context["history"] = history

        return EngineResponseDTO(
            text=reply,
            metadata={"engine": "openai", "model": "gpt-4o-mini", "tokens_used": tokens}
        )
