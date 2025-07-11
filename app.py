from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Bot Token from Telegram
TOKEN = os.environ.get("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Temporary in-memory storage for user data
user_profiles = {}

@app.route('/')
def home():
    return "✅ Mentor-CBA is up and running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip().lower()

        # Initialize new user
        if chat_id not in user_profiles:
            user_profiles[chat_id] = {"step": "ask_name", "profile": {}}

        user = user_profiles[chat_id]
        step = user["step"]
        profile = user["profile"]

        # Step-by-step career intake
        if step == "ask_name":
            user["step"] = "ask_degree"
            return send_message(chat_id, "👋 Welcome to Mentor-CBA!\nWhat's your full name?")

        elif step == "ask_degree":
            profile["name"] = text.title()
            user["step"] = "ask_college"
            return send_message(chat_id, "🎓 Wha
