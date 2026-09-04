import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit = request.args.get('deposit') or request.form.get('deposit')
    
    if trader_id:
        msg = f"✅ Deposit Verified!\nTrader ID: {trader_id}\nVIP Access Link: {VIP_LINK}"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    return jsonify({"status": "success"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Quotex VIP Bot is Running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
