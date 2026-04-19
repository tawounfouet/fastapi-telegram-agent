# 06 — Référence API

Ce document liste tous les contrats, schémas et interfaces du projet avec leurs signatures complètes.

---

## 📦 Schémas (DTOs) — `core/schemas.py`

Les DTOs (Data Transfer Objects) sont des objets **immuables et validés** qui transitent entre les couches.

### `UserDTO`

```python
class UserDTO(BaseModel):
    id: str               # ID Telegram de l'utilisateur (ex: "123456789")
    username: Optional[str] = None  # @username Telegram (peut être absent)
    is_bot: bool = False  # True si l'expéditeur est un bot
```

### `MessageDTO`

```python
class MessageDTO(BaseModel):
    id: str        # ID du message Telegram (ex: "42")
    user: UserDTO  # L'auteur du message
    text: str      # Contenu textuel du message
    timestamp: datetime  # UTC, généré automatiquement si absent
```

### `EngineResponseDTO`

```python
class EngineResponseDTO(BaseModel):
    text: str                        # Texte de la réponse du bot
    metadata: Dict[str, Any] = {}    # Infos optionnelles (engine utilisé, tokens, etc.)
```

**Exemple de metadata par engine :**
```python
# SimpleEngine
{"engine": "simple"}

# LLMEngineMock
{"engine": "llm_mock", "tokens_used": 42}

# OpenAIEngine (custom)
{"engine": "openai", "model": "gpt-4o", "tokens_used": 312}
```

---

## 🔌 Interfaces (Ports) — `core/interfaces/engine.py`

### `BaseEngine` — Interface des moteurs d'intelligence

```python
class BaseEngine(ABC):
    @abstractmethod
    async def process(
        self,
        message: MessageDTO,
        context: dict = None
    ) -> EngineResponseDTO:
        """
        Traite un message et retourne une réponse.

        Args:
            message : Le message de l'utilisateur (avec son texte et identité)
            context : Dictionnaire mutable contenant :
                      - history  : liste des échanges passés (max 10)
                      - tout autre état persisté par l'engine précédent

        Returns:
            EngineResponseDTO avec le texte de réponse et des métadonnées
        """
```

**Contrat implicite du `context` :**
```
context = {
    "history": [                      ← injecté par le Use Case
        {"user": "Bonjour", "bot": "🤖 Echo: Bonjour"},
        {"user": "Comment ça va ?", "bot": "🤖 Echo: Comment ça va ?"},
        ...
    ],
    "echo_count": 5,                  ← exemple de state custom (SimpleEngine)
    "last_topic": "météo",            ← exemple de state custom (vos engines)
    ...                               ← libre à vous d'ajouter des clés
}
```

### `MessageRepository` — Interface de l'historique des messages

```python
class MessageRepository(ABC):
    @abstractmethod
    async def save(
        self,
        message: MessageDTO,
        response: Optional[EngineResponseDTO] = None
    ) -> None:
        """Sauvegarde un message et sa réponse."""

    @abstractmethod
    async def get_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[dict]:
        """
        Retourne les N derniers échanges.
        Format : [{"user": "...", "bot": "..."}, ...]
        """
```

### `ContextRepository` — Interface de l'état conversationnel

```python
class ContextRepository(ABC):
    @abstractmethod
    async def get_context(self, user_id: str) -> dict:
        """Retourne l'état courant de l'utilisateur. {} si absent."""

    @abstractmethod
    async def save_context(self, user_id: str, context: dict) -> None:
        """Met à jour l'état de l'utilisateur."""
```

---

## 🏗️ Classes principales

### `EngineRegistry` — `engines/registry.py`

```python
class EngineRegistry:
    def register(self, name: str, engine: BaseEngine) -> None:
        """Enregistre un engine sous un nom (ex: "simple", "llm")."""

    def get_engine(self, name: str) -> BaseEngine:
        """
        Retourne l'engine enregistré sous ce nom.
        Lève ValueError si le nom n'existe pas.
        """
```

### `ProcessMessageUseCase` — `application/use_cases/process_message.py`

```python
class ProcessMessageUseCase:
    def __init__(
        self,
        engine: BaseEngine,
        message_repo: MessageRepository,
        context_repo: ContextRepository
    ): ...

    async def execute(self, message: MessageDTO) -> EngineResponseDTO:
        """Point d'entrée principal : traite un message de bout en bout."""
```

### `TelegramController` — `adapters/telegram/controller.py`

```python
class TelegramController:
    def __init__(self, process_message_use_case: ProcessMessageUseCase): ...

    async def handle_update(self, update: Update) -> list[str]:
        """
        Traite un Update Telegram.
        Retourne une liste de chunks texte prêts à envoyer (ou [] si rien à envoyer).
        """
```

### `TelegramFormatter` — `delivery/formatters/telegram_formatter.py`

```python
class TelegramFormatter:
    MAX_MESSAGE_LENGTH = 4000  # Seuil de découpage (limite Telegram : 4096)

    @staticmethod
    def escape_markdown_v2(text: str) -> str:
        """Échappe les caractères spéciaux Telegram MarkdownV2."""

    @classmethod
    def format_response(cls, response: EngineResponseDTO) -> list[str]:
        """Retourne une liste de chunks formatés et découpés."""
```

---

## ⚙️ Configuration — `config/settings.py`

| Variable | Type | Défaut | Description |
|----------|------|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | `str` | `"DEFAULT_TOKEN_FOR_TESTING"` | Token BotFather (obligatoire en prod) |
| `WEBHOOK_URL` | `str` | `"https://example.com/webhook"` | URL publique pour le mode webhook |
| `DEFAULT_ENGINE` | `str` | `"simple"` | Nom de l'engine actif (`simple`, `llm`, ou custom) |
| `OPENAI_API_KEY` | `str` | `""` | Clé API OpenAI (optionnelle) |

**Toutes ces variables peuvent être surchargées dans `.env`** à la racine du projet.

---

## 🗄️ Modèles de persistence — `persistence/models.py`

Structures internes utilisées par les repositories (non exposées aux autres couches).

```python
@dataclass
class MessageRecord:
    message_id: str
    user_id: str
    user_text: str
    bot_text: Optional[str]
    timestamp: datetime
    metadata: Dict         # {"engine": "simple", ...}

@dataclass
class UserContext:
    user_id: str
    state: Dict            # État libre géré par les engines
    last_updated: datetime
```

---

## 🌐 Endpoints HTTP (mode Webhook)

| Méthode | URL | Description |
|---------|-----|-------------|
| `POST` | `/webhook` | Reçoit les updates Telegram (JSON) |
| `GET` | `/health` | Healthcheck — retourne `{"status": "ok"}` |

**Exemple de payload `/webhook` (envoyé par Telegram) :**
```json
{
  "update_id": 12345678,
  "message": {
    "message_id": 42,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "username": "thomas_awf"
    },
    "chat": {"id": 987654321, "type": "private"},
    "text": "Bonjour !"
  }
}
```

---

← [05 — Engines](./05_engines.md) | [README](./README.md)
