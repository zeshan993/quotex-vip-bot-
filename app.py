import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")
MY_CHAT_ID = "6877916305"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id') or "N/A"
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "0"
    
    # Deposit amount ko float number mein convert karna
    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 0.0

    # Minimum $20 deposit condition
    if deposit_amount >= 20:
        text_msg = (
            f"✅ New Deposit Verified!\n\n"
            f"👤 Trader ID: {trader_id}\n"
            f"💵 Deposit: ${deposit_amount:.2f}\n"
            f"🔗 VIP Link: {VIP_LINK}"
        )
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": MY_CHAT_ID, "text": text_msg}
        requests.post(url, json=payload)
    
    # Aggar deposit $20 se kam ho toh koi Telegram message nahi jayega
    return jsonify({"status": "success"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Quotex VIP Bot is Active!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
