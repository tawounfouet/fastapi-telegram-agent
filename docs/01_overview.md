# 01 — Vue d'ensemble du projet

## 🎯 Objectif

**fastapi_telegram_agent** est un squelette de bot Telegram production-ready conçu pour être :

- **Extensible** : ajouter un nouveau moteur d'intelligence (LLM, règles métier, workflow) sans toucher au reste du code.
- **Testable** : chaque couche est indépendante et peut être testée en isolation.
- **Flexible** : supporte deux modes de déploiement — **polling** (développement) et **webhook** (production via FastAPI).

---

## 🏗️ Philosophie : Architecture Hexagonale (Ports & Adapters)

Le projet applique le pattern **architecture hexagonale** (aussi appelé *Ports & Adapters* ou *Clean Architecture*).

L'idée centrale : **le cœur métier ne doit jamais dépendre des détails techniques** (Telegram, FastAPI, base de données…).

```
┌─────────────────────────────────────────────────────────┐
│                     MONDE EXTÉRIEUR                      │
│                                                          │
│    Telegram API  ←──────────────────────→  HTTP/Webhook  │
│         │                                       │        │
│    ┌────▼───────────────────────────────────────▼────┐   │
│    │             ADAPTERS (couche d'entrée)           │   │
│    │    polling.py         webhook.py (FastAPI)       │   │
│    └─────────────────────┬───────────────────────────┘   │
│                          │ Update Telegram                │
│    ┌─────────────────────▼───────────────────────────┐   │
│    │           CONTROLLER (normalisateur)             │   │
│    │              controller.py                       │   │
│    └─────────────────────┬───────────────────────────┘   │
│                          │ MessageDTO                     │
│    ┌─────────────────────▼───────────────────────────┐   │
│    │         APPLICATION (cas d'usage)                │   │
│    │           ProcessMessageUseCase                  │   │
│    └──────────┬──────────────────────────────────────┘   │
│               │                                           │
│        ┌──────▼──────┐    ┌──────────────────────┐       │
│        │   ENGINES    │    │     PERSISTENCE       │       │
│        │  (Intelligence) │    │  (Repositories)       │       │
│        └─────────────┘    └──────────────────────┘       │
│               │                                           │
│    ┌──────────▼──────────────────────────────────────┐   │
│    │              CORE (Interfaces & Schémas)         │   │
│    │          schemas.py   interfaces/engine.py       │   │
│    └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Structure des dossiers

```
fastapi_telegram_agent/
│
├── main.py                     ← Point d'entrée et injection de dépendances
│
├── config/
│   └── settings.py             ← Variables d'environnement (pydantic-settings)
│
├── core/                       ← 🧠 CŒUR MÉTIER (aucune dépendance externe)
│   ├── schemas.py              ← DTOs : UserDTO, MessageDTO, EngineResponseDTO
│   └── interfaces/
│       └── engine.py           ← Contrats abstraits : BaseEngine, MessageRepository, ContextRepository
│
├── application/                ← Cas d'usage (orchestration)
│   └── use_cases/
│       └── process_message.py  ← ProcessMessageUseCase
│
├── engines/                    ← Moteurs d'intelligence (implémentent BaseEngine)
│   ├── registry.py             ← Registre des engines disponibles
│   ├── simple/
│   │   └── engine.py           ← SimpleEngine (écho, pour tests)
│   └── llm/
│       └── engine.py           ← LLMEngineMock (simulation OpenAI)
│
├── adapters/                   ← Connexion avec Telegram
│   └── telegram/
│       ├── controller.py       ← Normalisateur Update → DTO
│       ├── polling.py          ← Mode polling (développement)
│       └── webhook.py          ← Mode webhook via FastAPI (production)
│
├── delivery/                   ← Formatage de la réponse pour Telegram
│   └── formatters/
│       └── telegram_formatter.py
│
├── persistence/                ← Stockage des messages et du contexte
│   ├── models.py               ← Dataclasses internes (MessageRecord, UserContext)
│   └── repositories/
│       └── in_memory.py        ← Implémentation en mémoire (prototype)
│
├── requirements.txt
└── docs/                       ← 📖 Documentation (vous êtes ici)
```

---

## 🔑 Concepts clés

| Concept | Rôle |
|---------|------|
| **DTO (Data Transfer Object)** | Objet neutre transportant les données entre couches (`MessageDTO`, `EngineResponseDTO`) |
| **Interface (Port)** | Contrat abstrait que chaque implémentation doit respecter (`BaseEngine`) |
| **Adapter** | Traduit le monde extérieur (Telegram) vers le langage interne du projet |
| **Engine** | Cerveau du bot — traite le message et génère une réponse |
| **Use Case** | Orchestre les appels : récupère le contexte → appelle l'engine → sauvegarde |
| **Registry** | Registre des engines disponibles, sélection par nom via `.env` |

---

## ➡️ Prochaine étape

→ [02 — Installation & Configuration](./02_getting_started.md)
