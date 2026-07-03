import os
import telebot
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@app.route('/', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I received your message!")

if __name__ == "__main__":
    app.run()
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print("DEBUG: Inside echo_all function") # Add this line
    bot.reply_to(message, "I received your message!")
