import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests_logic
from requests_logic import Notion_edit

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Telegram_bot():
    def __init__(self):
        pass

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            client = requests_logic.Dictionary(word=update.message.text)
            word, defs = client.getdefinition()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Choose definition number")


            definition = client.choosedefinition()
            sentence = client.getsentence()

            notion_handler = Notion_edit(word=word, definition=definition, sentence=sentence)
            notion_handler.loadwordtonotion()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"""Word {word} has been added to Notion)
                                                                                    Definiton: {definition}
                                                                                    Sentence: {sentence}""")
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))

    def runbot(self):
        load_dotenv("APIs.env")
        application = ApplicationBuilder().token(os.getenv("TELEGRAM_API")).build()
        start_handler = CommandHandler("start", self.start)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)
        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.run_polling()
