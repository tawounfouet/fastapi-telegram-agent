#!/bin/sh
set -e

MODE="${1:-webhook}"

if [ "$MODE" = "webhook" ]; then
    # Register webhook URL with Telegram before starting the server
    if [ -n "$WEBHOOK_URL" ] && [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        echo "Registering Telegram webhook: $WEBHOOK_URL"
        python - <<'PYEOF'
import asyncio, os, sys
from telegram import Bot

async def register_webhook():
    bot = Bot(os.environ["TELEGRAM_BOT_TOKEN"])
    await bot.initialize()
    result = await bot.set_webhook(
        url=os.environ["WEBHOOK_URL"],
        allowed_updates=["message", "callback_query"]
    )
    print(f"Webhook registered: {result}")
    await bot.shutdown()

asyncio.run(register_webhook())
PYEOF
    fi

    echo "Starting in webhook mode..."
    exec python main.py webhook
else
    echo "Starting in polling mode..."
    exec python main.py polling
fi
