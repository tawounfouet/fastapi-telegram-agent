#!/bin/zsh
# ─────────────────────────────────────────────
#  start_bot.sh  —  Lance le bot Telegram une seule instance
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/bot.pid"
LOG_FILE="$SCRIPT_DIR/bot.log"

# Si un PID existe déjà, vérifier si le process tourne encore
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⚠️  Le bot tourne déjà (PID: $OLD_PID)"
        echo "   Pour l'arrêter : ./stop_bot.sh"
        exit 1
    else
        echo "🧹 Nettoyage du PID obsolète ($OLD_PID)..."
        rm -f "$PID_FILE"
    fi
fi

# Tuer toute instance zombie restante
pkill -9 -f "python main.py" 2>/dev/null
sleep 1

# Activer le venv et lancer
source "$SCRIPT_DIR/.venv/bin/activate"
nohup python "$SCRIPT_DIR/main.py" polling > "$LOG_FILE" 2>&1 &
BOT_PID=$!
echo $BOT_PID > "$PID_FILE"

echo "✅ Bot démarré (PID: $BOT_PID)"
echo "📋 Logs : tail -f $LOG_FILE"
echo "🛑 Arrêt : ./stop_bot.sh"
