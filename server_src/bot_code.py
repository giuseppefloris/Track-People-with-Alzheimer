import logging
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
Token = ''


def bot_operations(update, client, userdata, message):
    bot.send_message(chat_id=userdata['chat_id'], text=message.payload.decode())
    update.message.reply_text('ciao')
    client.publish(MQTT_TOPIC, update.message.text)
    update.message.reply_text('Message published to MQTT topic.')


updater = Updater(token=Token, use_context=True)
dp = updater.dispatcher
bot = Bot(Token)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

updater.start_polling()
updater.idle()

'''
class BotController:
    def __init__(self, token, mqtt_topic):
        self.token = token
        self.mqtt_topic = mqtt_topic
        self.bot = Bot(token)
        self.updater = Updater(token=self.token, use_context=True)
        self.dp = self.updater.dispatcher

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))

    def start(self, update, context):
        update.message.reply_text("Hello! I'm your bot. Type something.")

    def echo(self, update, context):
        message = update.message.text
        self.bot.send_message(chat_id=update.message.chat_id, text=message)
        self.publish_to_mqtt(message)
        update.message.reply_text("Message published to MQTT topic.")

    def publish_to_mqtt(self, message):
        # Your MQTT publishing logic here
        pass

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    TOKEN = "your_bot_token_here"
    MQTT_TOPIC = "your_mqtt_topic_here"

    bot_controller = BotController(TOKEN, MQTT_TOPIC)
    bot_controller.run()
'''