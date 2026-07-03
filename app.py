import os
import telebot
from flask import Flask, request
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '!', 200
    return 'Forbidden', 403

@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    try:
        config = types.GenerateContentConfig(
            system_instruction="You are Elena, 42. Playful, teasing, sophisticated."
        )
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=message.text,
            config=config
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Elena is feeling a bit shy right now.")

# Webhook Setup
bot.remove_webhook()
bot.set_webhook(url='https://YOURUSERNAME.pythonanywhere.com/')