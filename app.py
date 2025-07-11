from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# In-memory user states
user_profiles = {}

@app.route('/')
def home():
    return "Mentor-CBA (AI Career Bot) is live."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "").strip()

        # Store past messages per user
        if chat_id not in user_profiles:
            user_profiles[chat_id] = {
                "history": []
            }

        user_profiles[chat_id]["history"].append({"role": "user", "content": user_text})

        # Trim history to last 6 messages
        if len(user_profiles[chat_id]["history"]) > 6:
            user_profiles[chat_id]["history"] = user_profiles[chat_id]["history"][-6:]

        # Call DeepSeek API
        ai_reply = ask_deepseek(user_profiles[chat_id]["history"])
        user_profiles[chat_id]["history"].append({"role": "assistant", "content": ai_reply})

        send_message(chat_id, ai_reply)

    return "ok"

def ask_deepseek(messages):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "You are Mentor-CBA, a brutally honest but caring AI career coach. You must guide, grill, teach, motivate, and track the user's goals to get top consulting and business analysis offers in India (18+ LPA) or Dubai (AED 12k+). You must act like a real human mentor, not a bot. Always reply intelligently and if the user is slacking, call it out."}] + messages
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, data=json.dumps(body))
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return "⚠️ Error talking to AI. Try again later."

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(TELEGRAM_API, json=payload)
    except:
        pass
