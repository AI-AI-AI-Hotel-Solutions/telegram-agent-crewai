import requests
import datetime

BASEROW_TOKEN = "XqIY4Ru5ELx2ifWKyFGfJVt0HPfEyyAP"
TABLE_ID = "589034"
API_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"

HEADERS = {
    "Authorization": f"Token {BASEROW_TOKEN}",
    "Content-Type": "application/json"
}

def registrar_os_baserow(dados):
    payload = {
        "Data/Hora": datetime.datetime.now().isoformat(),
        "E-mail Autor": "sined.marecas@gmail.com",
        "Nome do Hóspede": dados.get("Nome do Hóspede", ""),
        "Quarto": dados.get("Quarto", ""),
        "Data do Serviço": dados.get("Data do Serviço", ""),
        "Horário do Serviço": dados.get("Horário do Serviço", ""),
        "Tipo de Serviço": dados.get("Tipo de Serviço", ""),
        "Detalhes do Pedido": dados.get("Detalhes do Pedido", ""),
        "Prioridade": dados.get("Prioridade", "Normal")
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return "✅ OS registrada com sucesso!"
    else:
        return f"❌ Erro ({response.status_code}): {response.text}"
