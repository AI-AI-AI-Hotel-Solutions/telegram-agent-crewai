from flask import Flask, request
import requests
import traceback
from crew_config import process_message

TOKEN = '7504265835:AAGkAEHaMmBW59SlfQ0ga9XuUF-lsx83zRU'
TELEGRAM_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'Bot online!', 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '')

    try:
        reply = process_message(text)
    except Exception as e:
        reply = f"[Erro interno]\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}"

    requests.post(TELEGRAM_URL, json={'chat_id': chat_id, 'text': reply})
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

