import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

# Server start hotay hi automatic Telegram webhook set ho jayega
if BOT_TOKEN:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")

# Verified depositors ki dictionary
verified_deposits = {}

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "0"
    
    if not trader_id:
        return jsonify({"status": "error", "message": "trader_id missing"}), 400

    # Brackets aur URL encoded characters (%7B, %7D) saaf karna
    trader_id = str(trader_id).replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').strip()
    deposit_str = str(deposit_str).replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').replace('$', '').strip()

    # Agar placeholder aa jaye toh ignore karo
    if trader_id.lower() in ['trader_id', 'id', 'none', '']:
        return jsonify({"status": "ignored", "message": "placeholder received"}), 200

    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 0.0

    # Sirf $20 ya us se zyada deposit wali IDs save hongi
    if deposit_amount >= 20:
        verified_deposits[trader_id] = deposit_amount

    return jsonify({"status": "success"}), 200

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "ok"}), 200

    message = data['message']
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Step 1: Start command par welcome message aur Trader ID mangna
    if text.startswith('/start'):
        welcome_msg = (
            "👋 **Welcome to Zeeshan Q Text Trader VIP Bot!**\n\n"
            "Please **Send your trader ID** (e.g. 93056154):"
        )
        requests.post(url, json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
    else:
        # Step 2: User ki bheji hui ID check karna
        trader_id = text.replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').strip()

        if trader_id in verified_deposits:
            reply_msg = (
                f"✅ **Verified!**\n\n"
                f"Aapka VIP Channel Link yeh raha:\n{VIP_LINK}"
            )
        else:
            reply_msg = (
                f"❌ **Aapka trader ID wrong hai** ya aapka minimum deposit complete nahi hai!"
            )

        requests.post(url, json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "Markdown"})

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "VIP Bot is Active!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
