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
    return "Mentor-CBA Bot is alive!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').strip().lower()

        if chat_id not in user_profiles:
            user_profiles[chat_id] = {"step": "ask_name", "profile": {}}

        user = user_profiles[chat_id]
        step = user['step']
        profile = user['profile']

        if text == "/reset":
            del user_profiles[chat_id]
            return send_message(chat_id, "🔄 Profile reset. Let’s start again.")

        if step == "ask_name":
            user['step'] = "ask_education"
            return send_message(chat_id, "👋 Welcome to Mentor-CBA, your AI career mentor.\n\nWhat’s your full name?")

        elif step == "ask_education":
            profile['name'] = text.title()
            user['step'] = "ask_degree"
            return send_message(chat_id, "🎓 What degree are you pursuing (e.g., MBA in Digital Business)?")

        elif step == "ask_degree":
            profile['degree'] = text
            user['step'] = "ask_college"
            return send_message(chat_id, "🏫 Which college/university are you studying at?")

        elif step == "ask_college":
            profile['college'] = text
            user['step'] = "ask_graduation"
            return send_message(chat_id, "🎓 When will you graduate? (e.g., June 2026)")

        elif step == "ask_graduation":
            profile['graduation'] = text
            user['step'] = "ask_internships"
            return send_message(chat_id, "💼 Tell me about your past internships (e.g., Company - Role - Duration)")

        elif step == "ask_internships":
            profile['internships'] = text
            user['step'] = "ask_goals"
            return send_message(chat_id, "🚀 What are your career goals? Mention CTC target, preferred roles, location, abroad or India etc.")

        elif step == "ask_goals":
            profile['goals'] = text
            user['step'] = "ask_freetime"
            return send_message(chat_id, "⏰ How many hours/day can you give to career prep?")

        elif step == "ask_freetime":
            profile['freetime'] = text
            user['step'] = "ask_freetime_window"
            return send_message(chat_id, "📅 What’s your free window daily? (e.g., 6–9PM or 10am–1pm)")

        elif step == "ask_freetime_window":
            match = re.search(r'(\d{1,2})\s*(am|pm)?\s*(?:-|to)\s*(\d{1,2})\s*(am|pm)?', text)
            if match:
                start_hour = int(match.group(1))
                end_hour = int(match.group(3))
                profile["free_slots"] = f"{start_hour}:00 to {end_hour}:00"
                user["step"] = "ask_motivation"
                return send_message(chat_id, f"✅ Got it! You’re free from {start_hour}:00 to {end_hour}:00.\n\nWhat motivates you more? A) Praise & rewards B) Guilt, FOMO? (Type A or B)")
            else:
                return send_message(chat_id, "❌ Format unclear. Try like: 6–9PM or 10am to 1pm")

        elif step == "ask_motivation":
            profile['motivation'] = text.upper()
            user['step'] = "ask_weaknesses"
            return send_message(chat_id, "😓 What’s holding you back right now?")

        elif step == "ask_weaknesses":
            profile['weaknesses'] = text
            user['step'] = "completed"
            return send_message(chat_id, f"🎉 Done! Thanks {profile['name']}. Your personalized journey begins tonight.")

        elif step == "completed":
            return send_message(chat_id, "✅ Your profile is complete. Type /reset to start over.")

        return send_message(chat_id, "🤔 Let’s finish your profile first!")

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
    app.run(host="0.0.0.0", port=port, debug=True)

