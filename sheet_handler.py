import datetime
import requests

BACKEND_URL = "https://script.google.com/macros/s/SEU_DEPLOY_ID/exec"
EMAIL_AUTOR = "sined.marecas@gmail.com"

def registrar_os(dados):
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "acao": "registrar",
        "dados": {
            "Data/Hora": agora,
            "E-mail Autor": EMAIL_AUTOR,
            "Nome do Hóspede": dados.get("Nome do Hóspede", ""),
            "Quarto": dados.get("Quarto", ""),
            "Data do Serviço": dados.get("Data do Serviço", ""),
            "Horário do Serviço": dados.get("Horário do Serviço", ""),
            "Tipo de Serviço": dados.get("Tipo de Serviço", ""),
            "Detalhes do Pedido": dados.get("Detalhes do Pedido", ""),
            "Prioridade": dados.get("Prioridade", "Normal")
        }
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        if response.status_code == 200:
            return f"✅ OS registrada com sucesso para o hóspede {dados.get('Nome do Hóspede', '')}!"
        else:
            return f"❌ Erro ao registrar OS. Código: {response.status_code}"
    except Exception as e:
        return f"❌ Erro ao conectar com o Apps Script: {e}"

