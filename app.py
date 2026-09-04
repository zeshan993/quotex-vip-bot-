import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")
MY_CHAT_ID = "6877916305"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit = request.args.get('deposit') or request.form.get('deposit')
    
    if trader_id:
        text_msg = f"✅ New Deposit Verified!\n\n👤 Trader ID: {trader_id}\n💵 Deposit: ${deposit}\n🔗 VIP Link: {VIP_LINK}"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": MY_CHAT_ID, "text": text_msg}
        requests.post(url, json=payload)
        
    return jsonify({"status": "success"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Quotex VIP Bot is Active!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
