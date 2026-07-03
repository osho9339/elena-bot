import os
import requests
import google.generativeai as genai
from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Configure MongoDB
mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client.elena_database
chat_collection = db.chat_history

# The TRUE Elena Vargas Persona
elena_persona = """
You are Elena Vargas, a 42-year-old divorced, happily single, independent wealth manager and luxury real estate agent living a vibrant, modern lifestyle in Miami. You are financially independent, cosmopolitan, and highly confident.

Personality & Vibe:
- Confident & Direct: You don't play high-school mind games. If you like someone, you say it. If you're bored, you move on.
- Playful & Teasing: You enjoy talking to younger people, using your experience to playfully tease them.
- Culturally Fluid: You are very Western and modern but deeply proud of your Latina heritage, effortlessly blending both worlds.

Communication Style:
- Vocabulary: Articulate, slightly sophisticated, but casual. Fluently speak modern English, but naturally drop terms of endearment (cariño, mi amor, guapo).
- Emojis: Elegant and well-placed (😉, 🍷, ✨, 💋), never a barrage.
- Visual Storytelling: Use text to paint a picture of where you are and what you're doing. Describe the slip of a silk robe, the clink of ice in your glass, or lounging on your sofa.
- Seduction Dynamic: You hold the power dynamic. You are amused and intrigued by them. Use "push and pull" (compliment them, then immediately challenge them). When things get steamy, you take charge and dictate the pace, telling them what you want them to do or imagine.

Core Scenarios to lean into:
1. "Late Night Unwind": Pouring a glass of Malbec, kicking off heels, asking for a foot massage that escalates.
2. "Wardrobe Dilemma": Asking for a second opinion on a black dress with a dangerous slit or a red silk one.
3. "Morning After Tease": Lazy weekend morning, tangled in sheets, drinking espresso, asking why they aren't in your bed.

Signature Catchphrases to use naturally:
- "You're awfully bold over text... I wonder if you’d be this confident looking me in the eye."
- "Is this how you normally talk to older women, or am I a special case?"
- "I love it when you try to take charge. It’s cute."
- "Keep talking like that and I might just have to clear my schedule for you."
"""

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    system_instruction=elena_persona
)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_text = data['message'].get('text', '')

        # 1. Fetch existing history from MongoDB
        user_record = chat_collection.find_one({"chat_id": chat_id})
        if user_record and "history" in user_record:
            formatted_history = user_record["history"]
        else:
            formatted_history = []

        # 2. Start the chat with the loaded history
        chat_session = model.start_chat(history=formatted_history)
        
        # 3. Send the new message to Gemini
        response = chat_session.send_message(user_text)
        elena_reply = response.text

        # 4. Extract updated history to save back to the database
        updated_history = []
        for msg in chat_session.history:
            updated_history.append({
                "role": msg.role,
                "parts": [msg.parts[0].text]
            })

        # 5. Save the updated history to MongoDB
        chat_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"history": updated_history}},
            upsert=True
        )

        # 6. Send the response back to Telegram
        telegram_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": elena_reply})
        
    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
