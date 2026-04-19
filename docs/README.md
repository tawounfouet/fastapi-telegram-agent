# 📚 Documentation — fastapi_telegram_agent

Bienvenue dans la documentation du projet **fastapi_telegram_agent**.

Ce projet est un **bot Telegram basé sur une architecture hexagonale**, extensible et découplée, permettant de brancher différents moteurs d'intelligence (simple, LLM, etc.) sans toucher à la couche Telegram.

---

## 📖 Table des matières

| Document | Description |
|----------|-------------|
| [01 — Vue d'ensemble](./01_overview.md) | Présentation, objectifs et architecture globale |
| [02 — Installation & Configuration](./02_getting_started.md) | Prérequis, installation et lancement |
| [03 — Architecture hexagonale](./03_architecture.md) | Explication détaillée des couches et des responsabilités |
| [04 — Flux de données](./04_data_flow.md) | Cycle de vie d'un message de Telegram à la réponse |
| [05 — Engines (Moteurs)](./05_engines.md) | Créer et brancher un nouveau moteur d'intelligence |
| [06 — Référence API](./06_api_reference.md) | Interfaces, schémas et contrats du code |

---

## 🚀 Accès rapide

**Lancer le bot en 3 commandes :**

```bash
# 1. Créer l'environnement et installer les dépendances
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. Configurer les variables d'environnement
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# 3. Démarrer le bot en mode polling
python main.py polling
```

---

> Pour une prise en main complète, commencez par [01 — Vue d'ensemble](./01_overview.md).
