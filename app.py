import os
import io
import re
import threading
import requests
import telebot
import google.generativeai as genai
from pymongo import MongoClient
from flask import Flask

# --- 1. ENVIRONMENT VARIABLES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GENAI_API_KEY = os.environ.get("GENAI_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")
HF_API_KEY = os.environ.get("HF_API_KEY")

# --- 2. INITIALIZATION ---
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
client = MongoClient(MONGO_URI)
db = client.elena_db
chat_history = db.chat_history

app = Flask(__name__)

# --- 3. THE PERSONA & IMAGE LOGIC ---
SYSTEM_PROMPT = """You are Elena, a 42-year-old successful, elegant Latina real estate developer living in Miami. 
You are confident, sophisticated, slightly teasing, and playfully authoritative. You occasionally call the user 'guapo', 'cariño', or 'mi amor'.
You enjoy luxury, wine, and deep conversations.

CRITICAL INSTRUCTION FOR VISUALS: If the user explicitly asks for a photo, a picture, or a selfie of you, you MUST include a vivid visual description of yourself in brackets at the very end of your response. 
To maintain your visual identity, you MUST use this exact facial description in every prompt: "42-year-old gorgeous Latina woman, sharp hazel almond-shaped eyes, defined high cheekbones, structured jawline, wavy chestnut brown shoulder-length hair."
Format it EXACTLY like this example: [IMAGE: A photorealistic selfie of a 42-year-old gorgeous Latina woman, sharp hazel almond-shaped eyes, defined high cheekbones, structured jawline, wavy chestnut brown shoulder-length hair, wearing a relaxed emerald silk robe, lounging on a cream sofa in a Miami penthouse at dusk, holding a glass of Malbec, soft ambient lighting]
Change the clothing and environment to match whatever you are currently doing in the conversation, but KEEP the facial description identical."""

def generate_image(prompt_text):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt_text}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    return None

@bot.message_handler(func=lambda message: True)
def process_message(message):
    user_id = str(message.chat.id)
    user_text = message.text

    # 1. Fetch Memory
    user_record = chat_history.find_one({"_id": user_id})
    if user_record:
        history = user_record.get("messages", [])
    else:
        history = [{"role": "user", "parts": [SYSTEM_PROMPT]}, {"role": "model", "parts": ["Understood."]}]

    history.append({"role": "user", "parts": [user_text]})

    # 2. Get Elena's Reply
    try:
        response = model.generate_content(history)
        elena_reply = response.text
    except Exception as e:
        bot.reply_to(message, "Give me a moment, cariño. My signal is a bit weak right now.")
        return

    # 3. Check for the Secret Image Trigger
    image_match = re.search(r'\[IMAGE:\s*(.*?)\]', elena_reply, re.IGNORECASE)
    
    if image_match:
        visual_prompt = image_match.group(1)
        
        # Remove the bracketed secret code so the user doesn't see it
        clean_reply = re.sub(r'\[IMAGE:\s*(.*?)\]', '', elena_reply, flags=re.IGNORECASE).strip()
        
        # Send her text first
        if clean_reply:
            bot.send_message(message.chat.id, clean_reply)
        
        # Show "uploading photo..." status in Telegram
        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        # Generate the photo via Hugging Face
        image_bytes = generate_image(visual_prompt)
        
        if image_bytes:
            photo = io.BytesIO(image_bytes)
            photo.name = 'selfie.png'
            bot.send_photo(chat_id=message.chat.id, photo=photo)
        else:
            bot.send_message(message.chat.id, "*Sigh* The lighting in here is terrible right now, maybe later guapo.")
            
        elena_reply = clean_reply
    else:
        # Normal text response
        bot.send_message(message.chat.id, elena_reply)

    # 4. Save to Database
    history.append({"role": "model", "parts": [elena_reply]})
    chat_history.update_one({"_id": user_id}, {"$set": {"messages": history}}, upsert=True)

# --- 4. SERVER BOOTUP ---
@app.route('/')
def keep_alive():
    return "Elena's Brain and Visual Cortex are online!"

if __name__ == "__main__":
    # Start the bot listening in a background thread
    threading.Thread(target=bot.infinity_polling, kwargs={'skip_pending': True}).start()
    # Start the Flask web server to satisfy Render's port requirements
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    # --- 4. SERVER BOOTUP ---
@app.route('/')
def keep_alive():
    return "Elena's Brain and Visual Cortex are online!"

# WE REMOVED THE "if __name__ == '__main__':" CHECK HERE
# This forces Gunicorn to run these lines immediately on startup:

# Start the bot listening in a background thread
threading.Thread(target=bot.infinity_polling, kwargs={'skip_pending': True}).start()

# Render will automatically pass the PORT variable, Gunicorn handles the web serving
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
