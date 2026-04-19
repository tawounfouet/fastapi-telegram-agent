from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from adapters.telegram.controller import TelegramController

class TelegramPollingAdapter:
    def __init__(self, token: str, controller: TelegramController):
        self.token = token
        self.controller = controller
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
        
    def _setup_handlers(self):
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        self.app.add_handler(CommandHandler("start", self._handle_start))
        
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chunks = await self.controller.handle_update(update)
        for chunk in chunks:
            # Pour l'exemple, on envoie sans parse_mode s'il est mal formaté, 
            # mais on pourrait utiliser parse_mode="MarkdownV2" si le formatter est parfait
            await update.message.reply_text(text=chunk)
            
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bonjour ! Je suis le bot. Envoyez-moi un message.")

    def run(self):
        print("Démarrage en mode POLLING...")
        self.app.run_polling()
