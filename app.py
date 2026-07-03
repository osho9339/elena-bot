import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.route('/', methods=['POST'])
def webhook():
    # 1. Get the data from Telegram
    data = request.get_json()
    
    # 2. Extract the chat ID and text
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        
        # 3. Send the reply using a direct HTTP request (not the library)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "I received your message!"
        }
        requests.post(url, json=payload)
        
    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
