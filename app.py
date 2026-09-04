import os
import sqlite3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

if BOT_TOKEN:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")

# Database initialization
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            trader_id TEXT PRIMARY KEY,
            deposit REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    trader_id = request.args.get('trader_id') or request.form.get('trader_id')
    deposit_str = request.args.get('deposit') or request.form.get('deposit') or "20" # Default 20 rakha hai taaki miss na ho
    
    if not trader_id:
        return jsonify({"status": "error", "message": "trader_id missing"}), 400

    # Brackets aur URL encoded characters saaf karna
    trader_id = str(trader_id).replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').strip()
    deposit_str = str(deposit_str).replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').replace('$', '').strip()

    if trader_id.lower() in ['trader_id', 'id', 'none', '']:
        return jsonify({"status": "ignored", "message": "placeholder received"}), 200

    try:
        deposit_amount = float(deposit_str)
    except ValueError:
        deposit_amount = 20.0 # Agar deposit text na ho toh valid maan lo

    # Database mein save karna
    if deposit_amount >= 20:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO deposits (trader_id, deposit) VALUES (?, ?)', (trader_id, deposit_amount))
        conn.commit()
        conn.close()

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
            "Please **Send your trader ID** (e.g. 93056154):"
        )
        requests.post(url, json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
    
    elif text.startswith('/add '):
        # Secret command taaki aap chat se hi koi ID manually add kar saken: /add 90125450
        parts = text.split()
        if len(parts) > 1:
            manual_id = parts[1].strip()
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO deposits (trader_id, deposit) VALUES (?, ?)', (manual_id, 50.0))
            conn.commit()
            conn.close()
            requests.post(url, json={"chat_id": chat_id, "text": f"✅ Trader ID {manual_id} successfully whitelisted!"})
        else:
            requests.post(url, json={"chat_id": chat_id, "text": "⚠️ Please provide ID, e.g. /add 90125450"})
    
    else:
        trader_id = text.replace('%7B', '').replace('%7D', '').replace('{', '').replace('}', '').strip()

        # Database se check karna
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT deposit FROM deposits WHERE trader_id = ?', (trader_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            reply_msg = (
                f"✅ **Verified!**\n\n"
                f"Aapka VIP Channel Link yeh raha:\n{VIP_LINK}"
            )
        else:
            reply_msg = (
                f"❌ **Aapka trader ID wrong hai** ya aapka minimum deposit complete nahi hai!\n"
                f"Agar aapki purani ID hai aur masla hai, toh ensure karein ke aapka account mere link se ho."
            )

        requests.post(url, json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "Markdown"})

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "VIP Bot fully active and database connected!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
