#!/bin/zsh
# ─────────────────────────────────────────────
#  stop_bot.sh  —  Arrête proprement le bot
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/bot.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  Aucun bot en cours (pas de bot.pid)"
    pkill -9 -f "python main.py" 2>/dev/null && echo "🧹 Instances zombies tuées." || true
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    sleep 1
    rm -f "$PID_FILE"
    echo "🛑 Bot arrêté (PID: $PID)"
else
    echo "ℹ️  Le process $PID n'existe plus."
    rm -f "$PID_FILE"
fi
