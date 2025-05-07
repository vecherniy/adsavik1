import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

BOT_TOKEN = "7980299038:AAFANLDHKEZglhkDYocft-ONiwwkSZ8Fq3c"
CHANNEL_ID = "@adsavik_test"
DATA_FILE = 'posts.json'

def format_caption(data):
    header = f"📦 <b>{data['type']} | {data['name']}</b>"
    price = ""
    if data['price']:
        formatted_price = f"{int(data['price']):,}".replace(",", ".")
        price = f"\n💸 {formatted_price}₽"
    street = f"\n📍 {data['street']}"
    description = f"\n<blockquote>✏️ {data['description']}</blockquote>"
    category = " ".join([f"#{word.lstrip('#')}" for word in data['category'].split()])
    if data.get("link"):
        user_line = f"\n\n🔗 <a href=\"{data['link']}\">Перейти к товару</a>"
    else:
        user_line = f"\n\n👤 @{data['user']}"
    footer = '\n\n<a href="https://t.me/adsavik">🛩 ДОСКА ОБЪЯВЛЕНИЙ</a>'
    return f"{header}{price}{street}{description}\n{category}{user_line}{footer}"

def send_post_with_photos(data, files):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    caption = format_caption(data)
    media = []

    for idx, file in enumerate(files[:3]):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        media.append(("media", (filename, open(path, "rb"))))

    media_json = [{
        "type": "photo",
        "media": f"attach://{secure_filename(file.filename)}",
        "caption": caption if i == 0 else "",
        "parse_mode": "HTML"
    } for i, file in enumerate(files[:3])]

    response = requests.post(
        url,
        data={"chat_id": CHANNEL_ID, "media": json.dumps(media_json)},
        files=media
    )
    print("Ответ Telegram:", response.text)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/send-post', methods=['POST'])
def send_post():
    data = json.loads(request.form['json'])  # данные формы
    photos = request.files.getlist('photos')  # файлы

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

    try:
        if photos:
            send_post_with_photos(data, photos)
        else:
            send_text_only(data)
    except Exception as e:
        print("Ошибка при отправке:", e)

    return jsonify({"status": "ok"}), 200

def send_text_only(data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": format_caption(data),
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    print("Ответ Telegram:", response.text)

if __name__ == '__main__':
    app.run(debug=True)
