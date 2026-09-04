import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

# Server start hotay hi automatic Telegram webhook set ho jayega
if BOT_TOKEN:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")

# Yahan sabhi verified depositors ka data save rahega
verified_deposits = {}

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    # Quotex se aane wale data ke brackets ya parameters handle karna
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "0"
    
    if not trader_id:
        return jsonify({"status": "error", "message": "trader_id missing"}), 400

    # Agar brackets ya extra text aa jaye toh usay clean karna
    trader_id = str(trader_id).replace('{', '').replace('}', '').strip()
    deposit_str = str(deposit_str).replace('{', '').replace('}', '').strip()

    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 0.0

    # Database mein Trader ID ke against deposit save kar liya
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

    if text.startswith('/start'):
        welcome_msg = (
            "👋 **Welcome to Zeeshan Q Text Trader VIP Bot!**\n\n"
            "VIP access hasil karne ke liye apni **Trader ID** yahan direct send karein (e.g. `93056154`).\n\n"
            "Bot khud aapka deposit check karke aapko VIP link provide kar dega!"
        )
        requests.post(url, json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
    else:
        # User ne jo text bheja hai usay Trader ID maankar check karo
        trader_id = text.replace('{', '').replace('}', '').strip()
        deposit = verified_deposits.get(trader_id, 0.0)

        if deposit >= 20:
            reply_msg = (
                f"✅ **Deposit Verified Successfully!**\n\n"
                f"👤 Trader ID: `{trader_id}`\n"
                f"💵 Total Deposit: ${deposit:.2f}\n\n"
                f"🔗 Aapka VIP Channel Link:\n{VIP_LINK}"
            )
        else:
            reply_msg = (
                f"❌ **Deposit Not Found or Insufficient!**\n\n"
                f"👤 Trader ID: `{trader_id}`\n"
                f"💵 Current Deposit Recorded: ${deposit:.2f}\n\n"
                f"⚠️ VIP access ke liye minimum $20 ka deposit hona lazmi hai. "
                f"Agar aapne deposit kar liya hai toh thora wait karein, system update ho jayega."
            )

        requests.post(url, json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "Markdown"})

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Interactive Quotex VIP Bot is Active!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
