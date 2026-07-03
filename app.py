import os
import telebot
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

# Example handler: This MUST be in your app.py
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # This sends the reply back to Telegram
    bot.reply_to(message, "I received your message!")

if __name__ == "__main__":
    app.run()