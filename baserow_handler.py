import datetime
import requests
from crewai.tools import tool

# Substitua pelos seus dados reais
API_TOKEN = "XqIY4Ru5ELx2ifWKyFGfJVt0HPfEyyAP"
TABLE_ID = "589034"
BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def prioridade_para_id(texto):
    mapa = {
        "Normal": 3616249,
        "Urgente": 3616250,
        "Atenção": 3616251
    }
    return mapa.get(texto, 3616249)  # Default: Normal


def registrar_os(dados):
    agora = datetime.datetime.now().isoformat()

    payload = {
    "field_4761397": agora,  # Data/Hora
    "field_4761405": "sined.marecas@gmail.com",  # E-mail Autor
    "field_4761406": dados.get("Nome do Hóspede", ""),
    "field_4761407": dados.get("Quarto", ""),
    "field_4761412": dados.get("Data do Serviço", ""),
    "field_4761414": dados.get("Horário do Serviço", ""),
    "field_4761415": dados.get("Tipo de Serviço", ""),
    "field_4761417": dados.get("Detalhes do Pedido", ""),
    "field_4761418": prioridade_para_id(dados.get("Prioridade", "Normal"))
}


    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        if response.status_code == 200 or response.status_code == 201:
            return "✅ OS registrada com sucesso!"
        else:
            return f"❌ Erro ({response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ Erro na requisição: {e}"


def consultar_os(filtros):
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            dados = response.json()["results"]
            resultados = []
            for row in dados:
                if all(str(row.get(k, "")).lower() == str(v).lower() for k, v in filtros.items()):
                    resultados.append(row)
            return f"🔍 {len(resultados)} resultado(s):\n\n" + "\n\n".join(str(r) for r in resultados) if resultados else "Nenhuma OS encontrada."
        else:
            return f"❌ Erro ao consultar OS ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na consulta: {e}"


def editar_os(criterios, novos_dados):
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            rows = response.json()["results"]
            for row in rows:
                if all(str(row.get(k, "")).lower() == str(v).lower() for k, v in criterios.items()):
                    row_id = row["id"]
                    update_response = requests.patch(f"{BASE_URL}{row_id}/", headers=HEADERS, json=novos_dados)
                    if update_response.status_code == 200:
                        return "✏️ OS atualizada com sucesso."
                    else:
                        return f"❌ Erro ao atualizar: {update_response.status_code}"
            return "OS não encontrada para edição."
        else:
            return f"❌ Erro na busca ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na edição: {e}"


def excluir_os(criterios):
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            rows = response.json()["results"]
            for row in rows:
                if all(str(row.get(k, "")).lower() == str(v).lower() for k, v in criterios.items()):
                    row_id = row["id"]
                    delete_response = requests.delete(f"{BASE_URL}{row_id}/", headers=HEADERS)
                    if delete_response.status_code == 204:
                        return "🗑️ OS excluída com sucesso."
                    else:
                        return f"❌ Erro ao excluir: {delete_response.status_code}"
            return "OS não encontrada para exclusão."
        else:
            return f"❌ Erro ao buscar OS ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na exclusão: {e}"




@tool("Executar ação no Baserow")
def executar_acao(json_resultado: dict) -> str:
    """Executa ações no Baserow com base no JSON estruturado retornado pelo agente Comandante."""
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

