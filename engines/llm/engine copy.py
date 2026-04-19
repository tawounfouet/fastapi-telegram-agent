from core.interfaces import BaseEngine
from core.schemas import MessageDTO, EngineResponseDTO
from config import settings


class LLMEngineMock(BaseEngine):
    """
    Mock d'un moteur LLM (ex: OpenAI).
    Permet de simuler un temps de réponse et une génération.
    """

    async def process(
        self, message: MessageDTO, context: dict = None
    ) -> EngineResponseDTO:
        # Dans un vrai cas, on appellerait le client OpenAI asynchrone ici
        # api_key = settings.OPENAI_API_KEY

        # Simulation d'une analyse basée sur l'historique
        history_length = len(context.get("history", [])) if context else 0

        response_text = f"🧠 [LLM Mock] J'ai analysé : '{message.text}'. "
        if history_length > 0:
            response_text += f"Je me souviens de {history_length} échanges précédents."

        return EngineResponseDTO(
            text=response_text, metadata={"engine": "llm_mock", "tokens_used": 42}
        )
