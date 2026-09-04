import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

# Server start hotay hi automatic Telegram webhook set ho jayega
if BOT_TOKEN:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")

# Temporary memory verified deposits ke liye
verified_deposits = {}

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "0"
    
    if not trader_id:
        return jsonify({"status": "error", "message": "trader_id missing"}), 400

    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 0.0

    verified_deposits[str(trader_id).strip()] = deposit_amount
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

    if text.startswith('/start'):
        welcome_msg = (
            "👋 Welcome to Zeeshan Q Text Trader VIP Bot!\n\n"
            "Apni **Trader ID** yahan send karein (e.g. 123456) taaki hum aapka deposit check karke VIP link provide kar sakein."
        )
        requests.post(url, json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
    else:
        trader_id = text
        deposit = verified_deposits.get(trader_id, 0.0)

        if deposit >= 20:
            reply_msg = (
                f"✅ **Deposit Verified Successfully!**\n\n"
                f"👤 Trader ID: `{trader_id}`\n"
                f"💵 Deposit: ${deposit:.2f}\n\n"
                f"🔗 Aapka VIP Channel Link:\n{VIP_LINK}"
            )
        else:
            reply_msg = (
                f"❌ **Verification Failed!**\n\n"
                f"👤 Trader ID: `{trader_id}`\n"
                f"💵 Current Deposit: ${deposit:.2f}\n\n"
                f"⚠️ VIP access ke liye minimum $20 ka deposit zaroori hai. "
                f"Pehle deposit mukammal karein phir apni ID yahan bhejein."
            )

        requests.post(url, json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "Markdown"})

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Interactive Quotex VIP Bot is Active!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
