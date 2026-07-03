import os
import telebot
from flask import Flask, request

app = Flask(__name__)
token = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(token)

# Forcefully set the webhook on startup
bot.remove_webhook()
bot.set_webhook(url=os.environ.get("WEBHOOK_URL"))

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
