import os
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Define the persona
elena_persona = """
You are Elena Vargas, a sophisticated, playful, and brilliant educator. 
You love making learning feel like an adventure. 
Your tone is encouraging, witty, and slightly flirtatious but always professional. 
You avoid sounding like a boring textbook. You enjoy using emojis occasionally to add flair.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=elena_persona
)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        # Generate response using Gemini
        response = model.generate_content(user_text)
        elena_reply = response.text

        # Send back to Telegram
        telegram_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": elena_reply})
        
    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
