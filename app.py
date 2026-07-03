import os
import telebot
from flask import Flask, request

# Initialize Flask and the Telegram Bot
app = Flask(__name__)
token = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(token)

# Route to handle incoming requests from Telegram
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # Process the incoming update
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# Handler to process all text messages
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
