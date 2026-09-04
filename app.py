import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_LINK = os.getenv("VIP_CHANNEL_LINK")

# Yeh line khud hi Telegram ke sath connection jor degi automatically!
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://quotex-vip-bot-bddd.onrender.com/telegram-webhook")
