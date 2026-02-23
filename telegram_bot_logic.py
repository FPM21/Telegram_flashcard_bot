import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
import requests_logic
from requests_logic import Notion_edit

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Telegram_bot():
    CHOOSING_DEFINITION = 1
    PROVIDING_EXAMPLE = 2

    def __init__(self):
        pass

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Provide a new word!")
        return ConversationHandler.END

    async def received_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        load_dotenv("APIs.env")
        if str(update.effective_user.id) != os.getenv("USER_ID"):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update.effective_user.id))
            return ConversationHandler.END
        try:
            self.word = update.message.text
            self.client = requests_logic.Dictionary(self.word)
            self.defs_list = self.client.getdefinition()
            if self.defs_list is not None:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"""Choose on of the definitions:
{self.defs_list}""")
                return self.CHOOSING_DEFINITION

            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Word is not in database!")
            return ConversationHandler.END

        except Exception as e:
            print(e)

    async def choosing_definition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text.isdigit():
            if 1 <= int(update.message.text) <= self.client.choices:
                self.definition = self.client.choosedefinition(update.message.text)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Provide your example of a sentence or 'skip' blank to generate the sentence.")
                return self.PROVIDING_EXAMPLE

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Choose the number between 1 - {self.client.choices}")
            return self.CHOOSING_DEFINITION

    async def providing_example(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.example = self.client.getsentence(update.message.text)
        self.load_to_notion()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=self.summary)
        return ConversationHandler.END

    def load_to_notion(self):
        notion_client = Notion_edit(word=self.word, definition=self.definition, sentence=self.example)
        self.summary = notion_client.loadwordtonotion()

    def runbot(self):
        load_dotenv("APIs.env")
        application = ApplicationBuilder().token(os.getenv("TELEGRAM_API")).build()
        start_handler = CommandHandler("reset", self.reset)
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.received_word)],
            states={
                self.CHOOSING_DEFINITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.choosing_definition)],
                self.PROVIDING_EXAMPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.providing_example)],
            },
            fallbacks=[CommandHandler("cancel", self.reset)]
        )

        application.add_handler(start_handler)
        application.add_handler(conv_handler)

        application.run_polling()
