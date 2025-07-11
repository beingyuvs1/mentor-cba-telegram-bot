from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

user_profiles = {}

@app.route('/')
def home():
    return "Mentor-CBA Phase 2 is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').strip()

        # Initialize user if new
        if chat_id not in user_profiles:
            user_profiles[chat_id] = {"step": "ask_name", "profile": {}}

        user = user_profiles[chat_id]
        step = user["step"]
        profile = user["profile"]

        if text.lower() == "/reset":
            del user_profiles[chat_id]
            return send_message(chat_id, "🔄 Profile reset. Let’s start again.\n\nWhat’s your full name?")

        # Step-by-step flow
        if step == "ask_name":
            profile["name"] = text
            user["step"] = "ask_degree"
            return send_message(chat_id, "🎓 What degree are you pursuing (e.g., MBA in Digital Business)?")

        elif step == "ask_degree":
            profile["degree"] = text
            user["step"] = "ask_college"
            return send_message(chat_id, "🏫 Which college/university are you studying at?")

        elif step == "ask_college":
            profile["college"] = text
            user["step"] = "ask_graduation"
            return send_message(chat_id, "🎓 When will you graduate? (e.g., June 2026)")

        elif step == "ask_graduation":
            profile["graduation"] = text
            user["step"] = "ask_internships"
            return send_message(chat_id, "💼 Tell me about your past internships (e.g., Company - Role - Duration)")

        elif step == "ask_internships":
            profile["internships"] = text
            user["step"] = "ask_goals"
            return send_message(chat_id, "🚀 What are your career goals?\nMention: roles, CTC target, location preferences, abroad or India etc.")

        elif step == "ask_goals":
            profile["goals"] = text
            user["step"] = "ask_freetime"
            return send_message(chat_id, "⏰ How many hours/day can you realistically give to your career prep?")

        elif step == "ask_freetime":
            profile["freetime"] = text
            user["step"] = "ask_freetime_window"
            return send_message(chat_id, "🗓️ What’s your daily free time window? (e.g., 6–9PM or 10am–1pm)")

        elif step == "ask_freetime_window":
            match = re.search(r'(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)?\s*(?:to|-)\s*(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)?', text.lower())
            if match:
                start_hour = int(match.group(1))
                start_period = match.group(3) or ''
                end_hour = int(match.group(4))
                end_period = match.group(6) or ''
                if start_period == 'pm' and start_hour < 12:
                    start_hour += 12
                if end_period == 'pm' and end_hour < 12:
                    end_hour += 12
                profile["free_slots"] = f"{start_hour}:00 to {end_hour}:00"
                user["step"] = "ask_motivation"
                return send_message(chat_id, f"✅ Got it! You're free from {start_hour}:00 to {end_hour}:00.\n\nWhat motivates you more?\nA) Praise & rewards\nB) FOMO, guilt, pressure\n(Type A or B)")
            else:
                return send_message(chat_id, "❌ I didn’t understand that. Please reply like:\n6–9PM or 10am–1pm")

        elif step == "ask_motivation":
            profile["motivation"] = text.upper()
            user["step"] = "ask_weaknesses"
            return send_message(chat_id, "😓 What’s holding you back right now? (e.g., Procrastination, fear, self-doubt)")

        elif step == "ask_weaknesses":
            profile["weaknesses"] = text
            user["step"] = "completed"
            return send_message(chat_id, f"✅ Got everything, {profile['name']}!\nYour custom AI mentor starts tonight. Be ready to get grilled daily. 🔥")

        elif step == "completed":
            return send_message(chat_id, "✅ Your profile is saved. Daily tracking starts soon. Type /reset to redo.")

        else:
            return send_message(chat_id, "⚠️ Let's finish your profile before anything else. Type /reset to restart.")

    return "ok"

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(URL, json=payload)
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
