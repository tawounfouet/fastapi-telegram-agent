# 04 — Flux de données

Ce document trace le cycle de vie complet d'un message, de son arrivée depuis Telegram jusqu'à la réponse envoyée à l'utilisateur.

---

## 🗺️ Vue générale du flux

```
Utilisateur Telegram
       │
       │  envoie "Bonjour !"
       ▼
┌─────────────────┐
│   Telegram API  │
└────────┬────────┘
         │
         │  Mode Polling       Mode Webhook
         │  (long-polling)     (HTTP POST)
         ▼                         ▼
┌─────────────────┐    ┌────────────────────────┐
│ TelegramPolling │    │ TelegramWebhookAdapter  │
│   Adapter       │    │  FastAPI /webhook       │
│ polling.py      │    │  webhook.py             │
└────────┬────────┘    └───────────┬────────────┘
         │                         │
         │  Update Telegram (objet brut)
         └────────────┬────────────┘
                      ▼
         ┌─────────────────────────┐
         │    TelegramController   │
         │    controller.py        │
         │                         │
         │  Update → MessageDTO    │
         │  UserDTO (id, username) │
         └──────────┬──────────────┘
                    │
                    │  MessageDTO
                    ▼
         ┌─────────────────────────┐
         │  ProcessMessageUseCase  │
         │  process_message.py     │
         │                         │
         │  1. get_context(uid)    │◄──── ContextRepository
         │  2. get_history(uid)    │◄──── MessageRepository
         │  3. engine.process()   │◄──── BaseEngine (simple/llm)
         │  4. save_context()     │────► ContextRepository
         │  5. save(msg, resp)    │────► MessageRepository
         └──────────┬──────────────┘
                    │
                    │  EngineResponseDTO
                    ▼
         ┌─────────────────────────┐
         │   TelegramFormatter     │
         │   telegram_formatter.py │
         │                         │
         │  Échappement MD v2      │
         │  Découpage (≤ 4000 car) │
         └──────────┬──────────────┘
                    │
                    │  ["chunk1", "chunk2", ...]
                    ▼
         ┌─────────────────────────┐
         │   Envoi vers Telegram   │
         │   reply_text() / bot.   │
         │   send_message()        │
         └─────────────────────────┘
                    │
                    ▼
       Utilisateur reçoit la réponse
```

---

## 🔍 Zoom sur chaque étape

### Étape 1 — Réception du message Telegram

**Fichier :** `adapters/telegram/polling.py` ou `adapters/telegram/webhook.py`

```
Mode POLLING
  └─ python-telegram-bot interroge https://api.telegram.org toutes les ~500ms
  └─ Quand un message arrive → callback _handle_message(update, context)

Mode WEBHOOK
  └─ Telegram envoie un POST sur https://votre-domaine.com/webhook
  └─ FastAPI reçoit la requête → handler async handle_webhook(request)
  └─ Update = Update.de_json(data, self.bot)
```

---

### Étape 2 — Normalisation (Controller)

**Fichier :** `adapters/telegram/controller.py`

L'`Update` Telegram brut contient de nombreux champs optionnels et dépendants de l'API Telegram.
Le controller l'extrait et le convertit en objets **purement métier** :

```
Update brut                          DTO métier
──────────────────────              ──────────────────────
update.message.from_user.id    →    UserDTO.id
update.message.from_user.username → UserDTO.username
update.message.from_user.is_bot →  UserDTO.is_bot
update.message.message_id      →    MessageDTO.id
update.message.text            →    MessageDTO.text
datetime.now(utc)              →    MessageDTO.timestamp
```

Si le message est vide ou n'a pas de texte → retourne `[]` sans appeler le use case.

---

### Étape 3 — Orchestration (Use Case)

**Fichier :** `application/use_cases/process_message.py`

C'est le chef d'orchestre. Il arrange les appels dans le bon ordre :

```
execute(message: MessageDTO)
    │
    ├── [1] context = context_repo.get_context(user_id)
    │         └─ Récupère l'état courant de l'utilisateur
    │            ex: {"echo_count": 3, "last_topic": "météo"}
    │
    ├── [2] history = message_repo.get_history(user_id, limit=10)
    │         └─ Récupère les 10 derniers échanges
    │            ex: [{"user": "salut", "bot": "🤖 Echo: salut"}, ...]
    │
    │   context["history"] = history  ← injecte l'historique dans le contexte
    │
    ├── [3] response = engine.process(message, context)
    │         └─ Le moteur génère une réponse
    │            EngineResponseDTO(text="...", metadata={...})
    │
    │   context.pop("history")  ← retire l'historique (évite la duplication)
    │
    ├── [4] context_repo.save_context(user_id, context)
    │         └─ Sauvegarde l'état mis à jour
    │
    └── [5] message_repo.save(message, response)
              └─ Sauvegarde l'échange complet (message + réponse)
```

---

### Étape 4 — Traitement par le moteur

**Fichier :** `engines/simple/engine.py` ou `engines/llm/engine.py`

Le moteur reçoit un `MessageDTO` et un `context: dict`, retourne un `EngineResponseDTO`.

```
SimpleEngine.process("Bonjour !", context)
    └─ retourne EngineResponseDTO(
           text="🤖 [Simple Engine] Echo: Bonjour !",
           metadata={"engine": "simple"}
       )

LLMEngineMock.process("Bonjour !", context)
    └─ Simule un appel LLM (ici, mock)
    └─ retourne EngineResponseDTO(
           text="🧠 [LLM Mock] J'ai analysé : 'Bonjour !'. Je me souviens de 2 échanges.",
           metadata={"engine": "llm_mock", "tokens_used": 42}
       )
```

---

### Étape 5 — Formatage et envoi

**Fichier :** `delivery/formatters/telegram_formatter.py`

```
EngineResponseDTO.text = "🤖 [Simple Engine] Echo: Bonjour !"
         │
         ▼
TelegramFormatter.format_response(response)
         │
         ├── escape_markdown_v2(text)
         │       └─ Échappe les caractères spéciaux : _ * [ ] ( ) ~ ` > # + - = | { } . !
         │
         └── Découpage en chunks de max 4000 caractères
                 └─ retourne ["chunk_1", "chunk_2", ...]  (souvent 1 seul chunk)
         │
         ▼
Adapter envoie chaque chunk via reply_text() ou bot.send_message()
```

---

## 📊 Tableau de correspondance des types

| Étape | Entrée | Sortie | Fichier |
|-------|--------|--------|---------|
| Réception | `HTTP POST` / `long-poll` | `Update` (python-telegram-bot) | polling.py / webhook.py |
| Normalisation | `Update` | `MessageDTO` | controller.py |
| Orchestration | `MessageDTO` | `EngineResponseDTO` | process_message.py |
| Intelligence | `MessageDTO` + `context dict` | `EngineResponseDTO` | engines/*/engine.py |
| Formatage | `EngineResponseDTO` | `list[str]` | telegram_formatter.py |
| Envoi | `list[str]` | Messages Telegram | polling.py / webhook.py |

---

## ➡️ Prochaine étape

→ [05 — Engines (Moteurs)](./05_engines.md)
