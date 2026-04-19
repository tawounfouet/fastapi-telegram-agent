# 02 — Installation & Configuration

## 📋 Prérequis

| Outil | Version minimale | Lien |
|-------|-----------------|------|
| Python | 3.11+ | [python.org](https://python.org) |
| pip | dernière version | inclus avec Python |
| Compte Telegram | — | [telegram.org](https://telegram.org) |
| Token BotFather | — | voir section ci-dessous |

---

## 🤖 Étape 0 — Créer votre bot Telegram

Avant tout, vous avez besoin d'un token de bot Telegram.

```
1. Ouvrez Telegram et cherchez @BotFather
2. Envoyez la commande : /newbot
3. Choisissez un nom pour votre bot (ex: "MonAgentTest")
4. Choisissez un username (doit finir par "bot", ex: "mon_agent_test_bot")
5. BotFather vous envoie le token :
   ┌──────────────────────────────────────────────────────┐
   │  Congratulations! Use this token to access the HTTP  │
   │  API: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz           │
   └──────────────────────────────────────────────────────┘
6. Copiez ce token → il sera votre TELEGRAM_BOT_TOKEN
```

---

## ⚙️ Étape 1 — Cloner et préparer l'environnement

```bash
# Cloner le projet (si pas déjà fait)
git clone <url-du-repo>
cd fastapi_telegram_agent

# Créer un environnement virtuel Python
python -m venv .venv

# Activer l'environnement
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Vérifier que Python est bien isolé
which python
# → /path/to/fastapi_telegram_agent/.venv/bin/python
```

---

## 📦 Étape 2 — Installer les dépendances

```bash
pip install -r requirements.txt
```

**Dépendances installées :**

| Package | Rôle |
|---------|------|
| `pydantic >= 2.4.2` | Validation et sérialisation des données (DTOs) |
| `pydantic-settings >= 2.0.3` | Chargement de la config depuis `.env` |
| `python-telegram-bot >= 20.6` | SDK Telegram (polling + webhook) |
| `fastapi >= 0.104.0` | Serveur web pour le mode webhook |
| `uvicorn >= 0.23.2` | Serveur ASGI pour FastAPI |

---

## 🔑 Étape 3 — Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```bash
touch .env
```

Editez-le avec les valeurs suivantes :

```bash
# .env

# ──────────────────────────────────────────────
#  OBLIGATOIRE : Token obtenu via BotFather
# ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# ──────────────────────────────────────────────
#  Moteur actif : "simple" ou "llm"
#  "simple" → écho du message (pour tester)
#  "llm"    → mock LLM (prêt pour brancher OpenAI)
# ──────────────────────────────────────────────
DEFAULT_ENGINE=simple

# ──────────────────────────────────────────────
#  Mode webhook uniquement (optionnel en dev)
# ──────────────────────────────────────────────
WEBHOOK_URL=https://votre-domaine.com/webhook

# ──────────────────────────────────────────────
#  LLM Engine (optionnel, pour le futur)
# ──────────────────────────────────────────────
OPENAI_API_KEY=sk-...
```

> ⚠️ Le fichier `.env` est dans `.gitignore` — ne le commitez jamais !

---

## 🚀 Étape 4 — Lancer le bot

### Mode Polling (recommandé en développement)

Le bot interroge l'API Telegram toutes les quelques secondes. Pas besoin d'une URL publique.

```bash
python main.py polling
# ou simplement (polling est le mode par défaut)
python main.py
```

Sortie attendue :
```
Démarrage en mode POLLING...
```

Ouvrez Telegram, envoyez `/start` puis un message → le bot répond immédiatement.

### Mode Webhook (recommandé en production)

Le bot reçoit les mises à jour via une requête HTTP POST sur `/webhook`. Nécessite une URL publique HTTPS.

```bash
python main.py webhook
```

Uvicorn démarre sur le port **8000** :
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**En développement local avec ngrok** (pour exposer localhost) :
```bash
# Dans un autre terminal :
ngrok http 8000

# L'URL publique fournie par ngrok ressemble à :
# https://abc123.ngrok.io

# Configurez ensuite le webhook Telegram :
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://abc123.ngrok.io/webhook"
```

---

## ✅ Vérification rapide

Voici comment vérifier que tout fonctionne :

```
Checklist :

[✓] python --version              → Python 3.11+
[✓] pip list | grep pydantic      → pydantic 2.x installé
[✓] cat .env | grep TOKEN         → Token présent
[✓] python main.py polling        → Démarrage sans erreur
[✓] Message envoyé sur Telegram   → Réponse du bot reçue
```

---

## 🔄 Changer de moteur rapidement

Pas besoin de toucher au code ! Modifiez simplement `.env` :

```bash
# Pour utiliser le mock LLM :
DEFAULT_ENGINE=llm

# Relancez le bot
python main.py
```

---

## ➡️ Prochaine étape

→ [03 — Architecture hexagonale](./03_architecture.md)
