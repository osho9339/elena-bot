import os
import telebot
from flask import Flask, request

app = Flask(__name__)
# Get token from environment variables
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # This forces the bot to process the incoming message
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# This handler listens for EVERY message
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")

if __name__ == "__main__":
    app.run()
