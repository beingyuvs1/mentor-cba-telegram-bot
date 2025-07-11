from flask import Flask, request
import re
import requests
import os

app = Flask(__name__)

# Bot Token from Telegram
TOKEN = os.environ.get("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# In-memory user data (temporary for Phase 2)
user_profiles = {}

@app.route('/')
def home():
    return "Mentor-CBA Phase 2 is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').strip().lower()

        # Initialize user profile if not already
        if chat_id not in user_profiles:
            user_profiles[chat_id] = {
                "step": "ask_name",
                "profile": {}
            }

        # Shortcut for current user
        user = user_profiles[chat_id]
        step = user['step']
        profile = user['profile']

        # STEP 1: Ask for name
        if step == "ask_name":
            user['step'] = "ask_education"
            return send_message(chat_id, "👋 Welcome to Mentor-CBA, your AI career mentor.\n\nLet’s begin by knowing you.\nWhat’s your full name?")

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
            return send_message(chat_id, "🚀 What are your career goals?\nMention: roles, CTC target, location preferences, abroad or India etc.")

        elif step == "ask_goals":
            profile['goals'] = text
            user['step'] = "ask_freetime"
            return send_message(chat_id, "⏰ How many hours/day can you realistically give to your career prep?\nMention when you're usually free (e.g., evenings 6–9PM)")

        elif step == "ask_freetime":
            profile['freetime'] = text
            user['step'] = "ask_freetime_window"
            return send_message(chat_id, "⏰ What’s your free time each day to work on your career?\nGive a daily window (e.g., 6–9PM or 10am–1pm).")

        elif step == "ask_freetime_window":
            match = re.search(r'(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)?\s*(?:to|-)\s*(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)?', text)
            if match:
                start_hour = int(match.group(1))
                start_period = match.group(3) or ''
                end_hour = int(match.group(4))
                end_period = match.group(6) or ''

                if start_period.lower() == 'pm' and start_hour < 12:
                    start_hour += 12
                if end_period.lower() == 'pm' and end_hour < 12:
                    end_hour += 12

                profile["free_slots"] = f"{start_hour}:00 to {end_hour}:00"
                user["step"] = "ask_motivation"
                return send_message(chat_id, f"✅ Got it! You’re free from {start_hour}:00 to {end_hour}:00 daily.\n\nNext — what motivates you more?\nA) Praise & rewards\nB) Guilt, comparison, or FOMO\n(Type A or B)")
            else:
                return send_message(chat_id, "❌ Couldn't understand that. Try like:\n6–9PM or 10am to 1pm")

        elif step == "ask_motivation":
            profile['motivation'] = text.upper()
            user['step'] = "ask_weaknesses"
            return send_message(chat_id, "😓 What’s holding you back right now?\n(e.g., Procrastination, self-doubt, distractions, lack of exposure, tech fear)")

        elif step == "ask_weaknesses":
            profile['weaknesses'] = text
            user['step'] = "completed"
            return send_message(chat_id, f"✅ Got everything, {profile['name']}!\nYour custom career engine starts tonight. Get ready.🔥")

        elif step == "completed":
            return send_message(chat_id, "✅ Your profile is already saved. Daily routine engine will start shortly. Type /reset to redo.")

        elif text == "/reset":
            del user_profiles[chat_id]
            return send_message(chat_id, "🔄 Profile reset. Let’s start again.")

        else:
            return send_message(chat_id, "I didn’t catch that. Let’s complete your profile first!")

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
