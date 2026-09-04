import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

if BOT_TOKEN:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")

# Verified depositors ki list jahan Quotex postback se data save hoga
verified_deposits = {}

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "0"
    
    if not trader_id:
        return jsonify({"status": "error", "message": "trader_id missing"}), 400

    trader_id = str(trader_id).replace('{', '').replace('}', '').strip()
    deposit_str = str(deposit_str).replace('{', '').replace('}', '').replace('$', '').strip()

    if trader_id.lower() in ['trader_id', 'id', 'none', '']:
        return jsonify({"status": "ignored", "message": "placeholder received"}), 200

    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 0.0

    # Sirf wahi IDs save hongi jinka deposit $20 ya us se zyada hoga
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

    # Step 1: Jab user /start kare
    if text.startswith('/start'):
        welcome_msg = (
            "👋 **Welcome!**\n\n"
            "Please **Send your trader ID** (e.g. 93056154):"
        )
        requests.post(url, json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
    else:
        # Step 2: Jab user apni Trader ID bhejey
        trader_id = text.replace('{', '').replace('}', '').strip()

        # Check karo ke kya yeh ID verified deposits ki list mein maujood hai?
        if trader_id in verified_deposits:
            reply_msg = (
                f"✅ **Verified!**\n\n"
                f"Aapka VIP Channel Link yeh raha:\n{VIP_LINK}"
            )
        else:
            # Agar ID galat ho ya deposit na ho
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
