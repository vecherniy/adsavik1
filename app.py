import json
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = 'posts.json'

BOT_TOKEN = "7980299038:AAFANLDHKEZglhkDYocft-ONiwwkSZ8Fq3c"
CHANNEL_ID = "@adsavik_test"  # или -100xxxxxxxxxx

def format_message(data):
    # Название и тип
    header = f"📦 <b>{data['type']} | {data['name']}</b>"

    # Цена (если есть)
    price = ""
    if data['price']:
        formatted_price = f"{int(data['price']):,}".replace(",", ".")
        price = f"\n💸 {formatted_price}₽"

    # Улица
    street = f"\n📍 {data['street']}"

    # Описание
    description = f"\n<blockquote>✏️ {data['description']}</blockquote>"


    # Теги
    category = " ".join([f"#{word.lstrip('#')}" for word in data['category'].split()])

    # 👤 или 🔗
    if data.get("link"):
        user_line = f"\n\n🔗 <a href=\"{data['link']}\">Перейти к товару</a>"
    else:
        user_line = f"\n\n👤 @{data['user']}"

    # Подвал
    footer = '\n\n<a href="https://t.me/adsavik">🛩 ДОСКА ОБЪЯВЛЕНИЙ</a>'

    return f"{header}{price}{street}{description}\n{category}{user_line}{footer}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    print("Ответ Telegram:", response.text)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/send-post', methods=['POST'])
def send_post():
    data = request.get_json()
    print("Данные с формы:", data)

    # Сохраняем в файл
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    else:
        posts = []

    posts.append(data)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    # Отправляем в Telegram
    try:
        send_telegram(format_message(data))
    except Exception as e:
        print("Ошибка при отправке в Telegram:", e)

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)
