from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from config import TELEGRAM_ACCESS_TOKEN, MONGO_DATABASE, MONGO_URI, ENABLE_TRAIN
import logging
import os

class Bot:
    current_bot = None
    status = "OFF"

    def echo(self, bot, update):
        response = self.current_bot.get_response(update.message.text)
        if float(response.confidence) > 0.5:
            update.message.reply_text(str(response.text))
        else:
            update.message.reply_text('Ainda não sei responder esta pergunta')


    def initial_message(self, bot, update):
        update.message.reply_text('Oi, eu sou SMDbot, em que posso te ajudar?')


    def start_telegram(self):
        # Create Updater object and attach dispatcher to it
        updater = Updater(TELEGRAM_ACCESS_TOKEN)
        dispatcher = updater.dispatcher
        print("Bot started")
        # Add command handler to dispatcher
        start_handler = CommandHandler('start', self.initial_message)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
        # Start the bot
        updater.start_polling()
        # Run the bot until you press Ctrl-C
        updater.idle()
        print("Bot idle executed...")


    def start_chatterBot(self, data):
        self.status = "LOADING"
        self.current_bot = self.create_bot()
        if data is not None:
            self.create_corpus_directory(data)

        if(ENABLE_TRAIN):
            print("TRAINING")
            self.status = "TRAINING"
            self.train_bot()

        self.status = "STARTED"


    def create_bot(self):
        #chatbot = ChatBot('SMDbot', read_only=True)
        chatbot = ChatBot('SMDbot',
                          storage_adapter = "chatterbot.storage.MongoDatabaseAdapter",
                          database = MONGO_DATABASE,
                          database_uri = MONGO_URI)
        logging.basicConfig(level=logging.INFO)
        return chatbot


    def train_bot(self):
        trainer = ChatterBotCorpusTrainer(self.current_bot)
        trainer.train(
            'chatterbot.corpus.portuguese',
            'bot-corpus/smd.yml'
        )


    def create_corpus_directory(self, data):
        dir_name = 'bot-corpus'
        try:
            os.mkdir(dir_name)
            print("Successfully created the directory %s " % dir_name)
        except FileExistsError:
            print("Directory %s already exists " % dir_name)

        f = open('bot-corpus/smd.yml', 'w', encoding='UTF-8')
        f.write('categories:\n')
        f.write('- smd\n')
        f.write('conversations:\n')
        for d in data:
            f.write("- - " + d[0] + "\n")
            f.write("  - " + d[1] + "\n")

        f.write('\n')
        f.close()
