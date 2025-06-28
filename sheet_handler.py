import requests
import datetime

# Substitua esta URL pelo link do seu Web App publicado no Apps Script
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxx-2ipOcJ4dl1cm-FIGZorV0TxF7xkfmdS3ZPId-5JeriYQ1BWg-16qKzqQI9gZCty/exec"

EMAIL_AUTOR = "sined.marecas@gmail.com"

def executar_acao(json_resultado):
    if not isinstance(json_resultado, dict) or "acao" not in json_resultado:
        return "Ação inválida ou não reconhecida."

    acao = json_resultado["acao"]
    payload = {"acao": acao}

    if acao == "registrar":
        dados = json_resultado.get("dados", {})
        payload["dados"] = {
            "Nome do Hóspede": dados.get("Nome do Hóspede", ""),
            "Quarto": dados.get("Quarto", ""),
            "Data do Serviço": dados.get("Data do Serviço", ""),
            "Horário do Serviço": dados.get("Horário do Serviço", ""),
            "Tipo de Serviço": dados.get("Tipo de Serviço", ""),
            "Detalhes do Pedido": dados.get("Detalhes do Pedido", ""),
            "Prioridade": dados.get("Prioridade", "")
        }

    elif acao == "consultar":
        payload["filtros"] = json_resultado.get("filtros", {})

    elif acao == "editar":
        payload["criterios"] = json_resultado.get("criterios", {})
        payload["novos_dados"] = json_resultado.get("novos_dados", {})

    elif acao == "excluir":
        payload["criterios"] = json_resultado.get("criterios", {})

    else:
        return "⚠️ Ação não suportada."

    try:
        response = requests.post(SCRIPT_URL, json=payload)
        return response.text
    except Exception as e:
        return f"❌ Erro na comunicação com Apps Script: {e}"

