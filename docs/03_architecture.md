# 03 — Architecture Hexagonale

## 🧩 Principe fondamental

L'architecture hexagonale repose sur une règle unique :

> **Les dépendances ne pointent que vers le centre (le Core).**
> Le Core ne connaît rien du monde extérieur.

```
              ┌──────────────────────────────────┐
              │      MONDE EXTÉRIEUR              │
              │  (Telegram, HTTP, BDD, OpenAI)   │
              └──────────┬───────────────────────┘
                         │
              ┌──────────▼───────────────────────┐
              │         ADAPTERS                  │
              │  Traduit le monde → DTO            │
              │  (telegram/polling, webhook)      │
              └──────────┬───────────────────────┘
                         │ MessageDTO
              ┌──────────▼───────────────────────┐
              │       APPLICATION                 │
              │  Orchestre les cas d'usage        │
              │  (ProcessMessageUseCase)          │
              └──────┬───────────────────────────┘
                     │               │
       ┌─────────────▼──┐   ┌────────▼──────────┐
       │    ENGINES      │   │   PERSISTENCE      │
       │ (Intelligence) │   │ (Repositories)     │
       └─────────────▲──┘   └────────▲──────────┘
                     │               │
              ┌──────┴───────────────┴───────────┐
              │            CORE                   │
              │  Interfaces (Ports) + Schémas     │
              │  Ne dépend de rien d'autre        │
              └──────────────────────────────────┘
```

---

## 🗂️ Description de chaque couche

### 1. 🟣 CORE — Le cœur immuable

**Fichiers :** `core/schemas.py`, `core/interfaces/engine.py`

C'est la couche la plus importante. Elle définit :
- Les **schémas de données** (DTOs) partagés par tout le projet
- Les **interfaces abstraites** (contrats) que les autres couches doivent implémenter

```
core/
├── schemas.py          ← UserDTO, MessageDTO, EngineResponseDTO
└── interfaces/
    └── engine.py       ← BaseEngine, MessageRepository, ContextRepository
```

**Règle d'or :** Le Core ne fait aucun import externe. Uniquement `abc`, `pydantic`, `typing`, `datetime`.

**Exemple de contrat (interface) :**
```python
class BaseEngine(ABC):
    @abstractmethod
    async def process(self, message: MessageDTO, context: dict = None) -> EngineResponseDTO:
        pass
```

Tout engine doit implémenter cette méthode. L'application ne sait rien de comment c'est fait à l'intérieur.

---

### 2. 🔵 ENGINES — Le cerveau du bot

**Fichiers :** `engines/simple/engine.py`, `engines/llm/engine.py`, `engines/registry.py`

Les engines implémentent l'interface `BaseEngine`. C'est ici que réside toute l'intelligence du bot.

```
engines/
├── registry.py         ← EngineRegistry : sélectionne l'engine actif
├── simple/
│   └── engine.py       ← SimpleEngine : écho basique (dev/test)
└── llm/
    └── engine.py       ← LLMEngineMock : simule un LLM (ex: GPT)
```

**Le registre (`registry.py`) :**
```
EngineRegistry
    │
    ├── "simple"  ──→  SimpleEngine()
    ├── "llm"     ──→  LLMEngineMock()
    └── (futur)   ──→  OpenAIEngine() / WorkflowEngine() / ...

Sélection via : settings.DEFAULT_ENGINE  (valeur dans .env)
```

Ajouter un nouveau cerveau au bot = créer une classe qui hérite de `BaseEngine` et l'enregistrer dans le registry. **Aucun autre fichier à modifier.**

---

### 3. 🟢 APPLICATION — L'orchestrateur

**Fichiers :** `application/use_cases/process_message.py`

Contient les **cas d'usage** : la logique qui orchestre les appels entre le core, les engines et la persistence. Un use case ne sait pas d'où vient le message (Telegram ? HTTP ? CLI ?).

```
ProcessMessageUseCase.execute(message: MessageDTO)
         │
         ├─ 1. context_repo.get_context(user_id)   → récupère l'état utilisateur
         ├─ 2. message_repo.get_history(user_id)   → récupère l'historique
         ├─ 3. engine.process(message, context)    → génère la réponse
         ├─ 4. context_repo.save_context(...)      → met à jour le contexte
         └─ 5. message_repo.save(message, response)→ sauvegarde l'échange
```

---

### 4. 🟡 PERSISTENCE — La mémoire du bot

**Fichiers :** `persistence/repositories/in_memory.py`, `persistence/models.py`

Implémente les interfaces `MessageRepository` et `ContextRepository` du Core.
Actuellement en mémoire (prototype) — remplaceable par PostgreSQL, Redis, etc. **sans toucher au use case**.

```
Persistence
    ├── InMemoryMessageRepository
    │       └── storage: { user_id → [MessageRecord, ...] }
    │           Méthodes : save(), get_history()
    │
    └── InMemoryContextRepository
            └── storage: { user_id → UserContext }
                Méthodes : get_context(), save_context()
```

**Pour passer en base de données réelle :**
1. Créer `persistence/repositories/postgres.py`
2. Implémenter `MessageRepository` et `ContextRepository`
3. Remplacer dans `main.py` → C'est tout.

---

### 5. 🟠 ADAPTERS — La porte d'entrée Telegram

**Fichiers :** `adapters/telegram/`

L'adapter traduit le langage Telegram (`Update`) en langage métier (`MessageDTO`), et vice versa.

```
adapters/telegram/
├── controller.py    ← Normalisateur central (Update → DTO → Use Case)
├── polling.py       ← Mode dev : interroge Telegram périodiquement
└── webhook.py       ← Mode prod : reçoit les POST HTTP de Telegram
```

**Le Controller est le point d'articulation :**
```
polling.py  ──┐
              ├──→  TelegramController.handle_update(update)
webhook.py  ──┘          │
                          ├── Normalise en MessageDTO
                          ├── Appelle ProcessMessageUseCase
                          └── Formate la réponse via TelegramFormatter
```

---

### 6. ⚪ DELIVERY — Le formateur de sortie

**Fichiers :** `delivery/formatters/telegram_formatter.py`

Traduit la réponse du bot (`EngineResponseDTO`) en messages compatibles Telegram :
- Échappe les caractères spéciaux pour le MarkdownV2
- Découpe les messages trop longs (limite Telegram : 4096 caractères)

---

### 7. 🔧 CONFIG — La configuration centralisée

**Fichiers :** `config/settings.py`

Charge les variables d'environnement via `pydantic-settings`. Un seul point de vérité pour toute la configuration.

```python
# Usage dans n'importe quel fichier :
from config import settings
settings.TELEGRAM_BOT_TOKEN   # → "123456789:ABC..."
settings.DEFAULT_ENGINE       # → "simple" ou "llm"
```

---

## 🔄 Diagramme des dépendances (sens des imports)

```
main.py
  │
  ├──→ config.settings
  ├──→ persistence.repositories.in_memory
  ├──→ engines.registry
  ├──→ engines.simple.engine ──→ core.interfaces
  ├──→ engines.llm.engine    ──→ core.interfaces, config
  ├──→ application.use_cases.process_message ──→ core.interfaces, core.schemas
  └──→ adapters.telegram.*
            │
            ├──→ core.schemas
            ├──→ application.use_cases
            └──→ delivery.formatters.telegram_formatter ──→ core.schemas

CORE ←── (tout le monde pointe vers core, core ne pointe vers rien)
```

---

## ➡️ Prochaine étape

→ [04 — Flux de données](./04_data_flow.md)
