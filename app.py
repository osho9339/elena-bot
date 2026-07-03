import os
import telebot
from flask import Flask, request

app = Flask(__name__)
token = os.environ.get("TELEGRAM_BOT_TOKEN")
print(f"DEBUG: Token loaded is: {token}") # This will print to your logs
bot = telebot.TeleBot(token)

@app.route('/', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")
    return 'Forbidden', 403

# This handler listens for EVERY message
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")

if __name__ == "__main__":
    app.run()
