from core.interfaces import BaseEngine
from core.schemas import MessageDTO, EngineResponseDTO

class SimpleEngine(BaseEngine):
    """
    Moteur simple pour tests et fallback.
    Fait simplement écho du message avec un petit préfixe.
    """
    
    async def process(self, message: MessageDTO, context: dict = None) -> EngineResponseDTO:
        response_text = f"🤖 [Simple Engine] Echo: {message.text}"
        
        # Simple update du contexte si besoin
        if context is not None:
            count = context.get("echo_count", 0)
            context["echo_count"] = count + 1
            
        return EngineResponseDTO(
            text=response_text,
            metadata={"engine": "simple"}
        )
