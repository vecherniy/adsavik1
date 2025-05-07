from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ТВОЙ_ТОКЕН_ЗДЕСЬ"
CHAT_ID = os.environ.get("CHAT_ID") or "ТВОЙ_CHAT_ID_ЗДЕСЬ"

@app.route("/")
def home():
    return "Бот запущен!"

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Нет данных"}), 400

    # Форматирование
    header = f"🛒 <b>{data['header']}</b>\n"
    price = f"💰 {data['price']}\n" if data['price'] else ""
    contact = f"📱 {data['contact']}\n"
    quote_prefix = "✏️ "
    description = f"\n<blockquote>{quote_prefix}{data['description']}</blockquote>"

    msg = header + price + contact + description

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)

    if res.status_code != 200:
        return jsonify({"error": res.text}), 500

    return jsonify({"status": "ok"}), 200


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("Webhook от Telegram:", data)

    if "message" in data and data["message"].get("text") == "/start":
        chat_id = data["message"]["chat"]["id"]

        reply_markup = {
            "keyboard": [
                [{"text": "📋 Новое объявление", "web_app": {"url": "https://adsavik-bot.onrender.com"}}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }

        payload = {
            "chat_id": chat_id,
            "text": "👋 Привет! Чтобы подать объявление, нажми на кнопку ниже:",
            "reply_markup": reply_markup
        }

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)

    return jsonify({"status": "ok"}), 200
