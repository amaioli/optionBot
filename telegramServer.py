import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from apscheduler.schedulers.background import BackgroundScheduler

class TelegramServer():
    def __init__(self, sched: BackgroundScheduler):
        self.sched = sched
        self.logger = logging.getLogger(__name__)
        self.application = Application.builder().token("5619010758:AAH1lRQlgHrHnBZ_3bCEazq3vZY7mAd1SHo").build()  # TOKEN to be added in a config
        self.application.add_handler(CommandHandler("pause", self.pause))
        self.application.add_handler(CommandHandler("resume", self.resume))
        self.application.run_polling()

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Pause Bots"""
        for i in self.sched.get_jobs():
            i.pause()

        await update.message.reply_text("Bot paused")

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Resume Bots"""
        for i in self.sched.get_jobs():
            i.resume()

        await update.message.reply_text("Bot resumed")