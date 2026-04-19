# 05 — Engines (Moteurs d'Intelligence)

Les engines sont le point d'extension principal du projet. C'est ici que vous branchez votre logique métier : règles, LLM, workflows, etc.

---

## 🧠 Engines disponibles

### Engine 1 — SimpleEngine

**Fichier :** `engines/simple/engine.py`  
**Identifiant :** `"simple"` (dans `.env`)

Fait un écho du message reçu. Idéal pour les tests et le développement.

```
Entrée :  "Bonjour !"
Sortie :  "🤖 [Simple Engine] Echo: Bonjour !"

Mise à jour contexte :
  context["echo_count"] += 1   ← compteur d'échanges
```

---

### Engine 2 — LLMEngineMock

**Fichier :** `engines/llm/engine.py`  
**Identifiant :** `"llm"` (dans `.env`)

Simule un appel à un LLM (OpenAI, Anthropic, etc.). Exploite l'historique de conversation injecté dans le contexte.

```
Entrée :  "Parle-moi de Python"  + context.history (2 échanges)
Sortie :  "🧠 [LLM Mock] J'ai analysé : 'Parle-moi de Python'.
           Je me souviens de 2 échanges précédents."

Métadonnées :  {"engine": "llm_mock", "tokens_used": 42}
```

---

## 🔄 Registre des engines

**Fichier :** `engines/registry.py`

```
┌─────────────────────────────────────┐
│           EngineRegistry            │
│                                     │
│  _engines = {                       │
│    "simple" → SimpleEngine()        │
│    "llm"    → LLMEngineMock()       │
│    ...                              │
│  }                                  │
│                                     │
│  get_engine("simple") → BaseEngine  │
└─────────────────────────────────────┘
         ↑
         │  Rempli dans main.py via bootstrap()
         │
         registry.register("simple", SimpleEngine())
         registry.register("llm",    LLMEngineMock())
         │
         active = registry.get_engine(settings.DEFAULT_ENGINE)
```

---

## 🛠️ Créer un nouvel engine — Guide pas à pas

### Exemple : OpenAIEngine (brancher GPT-4 réel)

**Étape 1 : Créer le dossier et le fichier**

```
engines/
└── openai/
    ├── __init__.py     ← (vide)
    └── engine.py       ← votre code ici
```

**Étape 2 : Implémenter `BaseEngine`**

```python
# engines/openai/engine.py

from openai import AsyncOpenAI
from core.interfaces import BaseEngine
from core.schemas import MessageDTO, EngineResponseDTO
from config import settings


class OpenAIEngine(BaseEngine):
    """
    Moteur utilisant l'API OpenAI (GPT-4o, etc.)
    """

    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def process(self, message: MessageDTO, context: dict = None) -> EngineResponseDTO:
        # Construire les messages pour l'API OpenAI
        messages = []

        # Injecter l'historique de conversation
        if context and "history" in context:
            for exchange in context["history"]:
                messages.append({"role": "user",    "content": exchange["user"]})
                messages.append({"role": "assistant","content": exchange["bot"] or ""})

        # Ajouter le message actuel
        messages.append({"role": "user", "content": message.text})

        # Appel à l'API
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=500,
        )

        response_text = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens

        return EngineResponseDTO(
            text=response_text,
            metadata={
                "engine": "openai",
                "model": self.model,
                "tokens_used": tokens_used,
            }
        )
```

**Étape 3 : Enregistrer dans `main.py`**

```python
# main.py — dans la fonction bootstrap()

from engines.openai.engine import OpenAIEngine  # ← ajouter cet import

def bootstrap():
    # ...
    openai_engine = OpenAIEngine(model="gpt-4o")
    registry.register("openai", openai_engine)   # ← ajouter cette ligne
    # ...
```

**Étape 4 : Activer dans `.env`**

```bash
DEFAULT_ENGINE=openai
OPENAI_API_KEY=sk-proj-...
```

**Étape 5 : Installer le SDK OpenAI (si pas encore fait)**

```bash
pip install openai
# Ajouter dans requirements.txt :
echo "openai>=1.0.0" >> requirements.txt
```

**C'est tout !** Aucun autre fichier n'a besoin d'être modifié.

---

## 📐 Checklist pour un engine valide

```
[ ] Hérite de BaseEngine (from core.interfaces import BaseEngine)
[ ] Implémente async def process(self, message: MessageDTO, context: dict) -> EngineResponseDTO
[ ] Ne fait aucun import de Telegram ou FastAPI
[ ] Retourne toujours un EngineResponseDTO (jamais None)
[ ] Gère les exceptions (try/except) et retourne un fallback si l'API externe échoue
[ ] Enregistré dans registry via registry.register("nom", instance)
```

---

## 💡 Autres idées d'engines

| Nom | Description | Cas d'usage |
|-----|-------------|-------------|
| `RulesEngine` | Répond selon des règles if/else | FAQ, support client simple |
| `WorkflowEngine` | Enchaîne des étapes conditionnelles | Formulaires conversationnels |
| `AnthropicEngine` | Branche Claude (Anthropic) | Alternative à OpenAI |
| `RAGEngine` | Retrieval-Augmented Generation | Bot documentaire |
| `HuggingFaceEngine` | Modèles open source locaux | Confidentialité des données |

---

## ➡️ Prochaine étape

→ [06 — Référence API](./06_api_reference.md)
