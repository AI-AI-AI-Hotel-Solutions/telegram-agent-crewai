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
    try:
        message = data.get('message', {})
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if not text:
            return '', 200  # Ignora mensagens sem texto

        reply = process_message(text)
    except Exception as e:
        reply = f"[Erro interno]\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}"

    # Envia a resposta ao Telegram
    try:
        requests.post(TELEGRAM_URL, json={'chat_id': chat_id, 'text': reply})
    except Exception as e:
        print("[Erro ao enviar resposta para o Telegram]", e)

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
