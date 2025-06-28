import datetime
import requests

BACKEND_URL = "https://script.google.com/macros/s/AKfycbxx-2ipOcJ4dl1cm-FIGZorV0TxF7xkfmdS3ZPId-5JeriYQ1BWg-16qKzqQI9gZCty/exec"
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
    return enviar_requisicao(payload)


def consultar_os(filtros):
    payload = {
        "acao": "consultar",
        "filtros": filtros
    }
    return enviar_requisicao(payload)


def editar_os(criterios, novos_dados):
    payload = {
        "acao": "editar",
        "criterios": criterios,
        "novos_dados": novos_dados
    }
    return enviar_requisicao(payload)


def excluir_os(criterios):
    payload = {
        "acao": "excluir",
        "criterios": criterios
    }
    return enviar_requisicao(payload)


def enviar_requisicao(payload):
    print("[DEBUG] Enviando payload para Apps Script:", json.dumps(payload, indent=2, ensure_ascii=False))
    try:
        response = requests.post(BACKEND_URL, json=payload)
        print("[DEBUG] Status da resposta:", response.status_code)
        print("[DEBUG] Conteúdo da resposta:", response.text)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"❌ Erro ao conectar com Apps Script (Código {response.status_code})"
    except Exception as e:
        return f"❌ Erro na conexão: {e}"



# 🎯 Função principal que despacha a ação com base no JSON
def executar_acao(json_resultado):
    print("[DEBUG] JSON recebido:", json_resultado)  # 👈 Isso
    acao = json_resultado.get("acao", "")
    
    if acao == "registrar":
        return registrar_os(json_resultado.get("dados", {}))
    elif acao == "consultar":
        return consultar_os(json_resultado.get("filtros", {}))
    elif acao == "editar":
        return editar_os(
            json_resultado.get("criterios", {}),
            json_resultado.get("novos_dados", {})
        )
    elif acao == "excluir":
        return excluir_os(json_resultado.get("criterios", {}))
    else:
        return "❌ Ação inválida ou não suportada."
