import os
from flask import Flask, request
import requests
import traceback
from crew_config import process_message

# 🔐 Seu token do bot
TOKEN = '7042542286:AAG-zWG2eYLkayXyoxICPckkbvqorcvDHJQ'
TELEGRAM_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'Bot online!', 200

# 🔧 Corrigido: webhook agora é /webhook (não mais /)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📥 JSON recebido:", data)  # 👁️ Log útil para debug

    try:
        message = data.get('message', {})
        chat_id = message['chat']['id']
        text = message.get('text', '')
        print(f"💬 Texto recebido: {text}")
        print(f"👤 chat_id: {chat_id}")

        if not text:
            return '', 200

        # Normal: processa a mensagem com o agente
        reply = process_message(text)

        # 🧪 Alternativo para teste:
        # reply = f"Seu chat_id é: {chat_id}"

    except Exception as e:
        reply = f"[Erro interno]\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}"

    try:
        r = requests.post(TELEGRAM_URL, json={'chat_id': chat_id, 'text': reply})
        if r.status_code != 200:
            print(f"❌ Falha ao enviar para Telegram ({chat_id}): {r.status_code} - {r.text}")
    except Exception as e:
        print("[Erro ao enviar resposta para o Telegram]", e)

    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
