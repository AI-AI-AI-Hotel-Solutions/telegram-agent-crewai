import datetime
import requests
from crewai.tools import tool
import re
import unicodedata

# Token e base do Baserow
API_TOKEN = "GKCjjEjcTAQUNpgD9rc6O2VJGLqnKtjN"
TABLE_ID = "593203"
BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# Mapeamento dos campos legíveis para os field_xxx do Baserow
FIELD_MAP = {
    "Data/Hora": "field_4798728",
    "E-mail Autor": "field_4798733",
    "Nome do Hóspede": "field_4798734",
    "Quarto": "field_4798740",
    "Data do Serviço": "field_4798743",
    "Horário do Serviço": "field_4798756",
    "Tipo de Serviço": "field_4798778",
    "Detalhes do Pedido": "field_4798779",
    "Prioridade": "field_4798780",
    "Departamentos": "field_4865800"
}

# IDs dos departamentos
DEPARTAMENTOS = {
    "Concierge": 3681531,
    "Recepção": 3681532,
    "Bar": 3681533,
    "Salão": 3681534,
    "Cozinha": 3681535,
    "Governança": 3681536
}

# Sinônimos aceitos para campos
ALIASES = {
    "Nomes dos Hóspedes": "Nome do Hóspede",
    "Hospedes": "Nome do Hóspede",
    "Hóspedes": "Nome do Hóspede"
}

def prioridade_para_id(texto):
    texto = str(texto).strip().lower()
    mapa = {
        "normal": 3681527,
        "urgente": 3681528,
        "atenção": 3681529,
        "vip": 3681529,
        "cliente vip": 3681529,
        "cliente habitue": 3681530,
        "cliente habitual": 3681530
    }
    return mapa.get(texto, 3681527)

def serializar_detalhes(detalhes):
    if isinstance(detalhes, dict):
        partes = [f"{k}: {v}" for k, v in detalhes.items()]
        return "; ".join(partes)
    return str(detalhes)

def normalizar_data(data):
    try:
        if isinstance(data, str):
            data = data.strip().replace("/", "-")
            partes = data.split("-")
            if len(partes) == 3 and len(partes[0]) != 4:
                partes = partes[::-1]
            return "-".join(partes)
        return str(data)
    except:
        return str(data)

def inferir_departamentos(dados):
    texto = f"{dados.get('Tipo de Serviço', '')} {dados.get('Detalhes do Pedido', '')}".lower()
    deps = {"Concierge", "Recepção"}
    if any(palavra in texto for palavra in ["bolo", "comida", "menu", "café", "jantar", "almoço", "sobremesa"]):
        deps.update(["Cozinha", "Salão"])
    if any(palavra in texto for palavra in ["vinho", "drink", "coquetel", "bebida"]):
        deps.update(["Bar", "Salão"])
    if any(palavra in texto for palavra in ["servir", "serviço", "garçom"]):
        deps.add("Salão")
    if any(palavra in texto for palavra in ["decoração", "decorar", "arrumar", "flores"]):
        deps.add("Governança")
    return [DEPARTAMENTOS[d] for d in deps]

def mapear_campos(dados: dict) -> dict:
    mapeado = {}
    if "Prioridade" not in dados and "Status do Cliente" in dados:
        status = str(dados["Status do Cliente"]).strip().lower()
        dados["Prioridade"] = status

    for chave, valor in dados.items():
        chave = ALIASES.get(chave, chave)

        if chave == "Nome do Hóspede" and isinstance(valor, list):
            valor = " e ".join(valor)

        if chave == "Nome do Hóspede" and isinstance(valor, str) and " e " in valor.lower():
            nomes = [n.strip() for n in valor.split(" e ")]
            if len(nomes) >= 2:
                valor = nomes[0]
                detalhes_atuais = dados.get("Detalhes do Pedido", "")
                acompanhantes = f"Acompanhante(s): {', '.join(nomes[1:])}."
                dados["Detalhes do Pedido"] = f"{acompanhantes} {detalhes_atuais}".strip()

        id_campo = FIELD_MAP.get(chave)
        if not id_campo:
            continue

        if chave == "Prioridade":
            valor = prioridade_para_id(valor)
        elif chave == "Data do Serviço":
            valor = normalizar_data(valor)
        elif chave == "Detalhes do Pedido":
            valor = serializar_detalhes(valor)
        elif chave == "Quarto":
            numeros = re.findall(r"\d+", str(valor))
            valor = int(numeros[0]) if numeros else 0

        mapeado[id_campo] = valor

    # Adiciona campo Departamentos baseado no conteúdo
    mapeado[FIELD_MAP["Departamentos"]] = inferir_departamentos(dados)

    return mapeado

def formatar_os(os: dict) -> str:
    prioridade = os.get('field_4798780', {}).get('value', 'Normal')
    detalhes = os.get('field_4798779', '')
    data_servico = os.get('field_4798743', '---')
    criado_em = os.get('field_4798728', '')

    try:
        criado_dt = datetime.datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
        criado_formatado = f"{criado_dt.date()} às {criado_dt.strftime('%H:%M')}"
    except:
        criado_formatado = criado_em

    return f"""
- Quarto: {os.get('field_4798740', '---')}
- Data do Serviço: {data_servico}
- Horário: {os.get('field_4798756', '---')}
- Tipo de Serviço: {os.get('field_4798778', '---')}
- Detalhes do Pedido: {detalhes}
- Prioridade: {prioridade}
- Autor: {os.get('field_4798733', '---')}
- Criado em: {criado_formatado}
""".strip()

def registrar_os(dados):
    agora = datetime.datetime.now().isoformat()
    payload = mapear_campos(dados)
    payload[FIELD_MAP["Data/Hora"]] = agora
    payload[FIELD_MAP["E-mail Autor"]] = "teste@gmail.com"
    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        if response.status_code in [200, 201]:
            return "✅ OS registrada com sucesso!"
        else:
            return f"❌ Erro ({response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ Erro na requisição: {e}"


def normalizar_valor(valor):
    if isinstance(valor, dict):
        valor = valor.get("value", "")
    elif isinstance(valor, list):
        # Para listas (como Departamentos), transforma todos os itens em string normalizada
        return [normalizar_valor(v) for v in valor]
    return (
        unicodedata.normalize("NFKD", str(valor).strip().lower())
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )

def corresponde(row, filtros):
    for campo_legivel, valor_filtro in filtros.items():
        field_id = FIELD_MAP.get(campo_legivel, campo_legivel)
        valor_row = row.get(field_id)

        if valor_row is None:
            return False

        if isinstance(valor_row, dict):
            valor_row = valor_row.get("value", "")

        if isinstance(valor_filtro, dict):
            valor_filtro = valor_filtro.get("value", valor_filtro)

        if str(valor_row).strip().lower() != str(valor_filtro).strip().lower():
            return False

    return True



def consultar_os(filtros):
    print(f"[🔍] Consultando OS com filtros: {filtros}")
    filtros = mapear_campos(filtros)
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            dados = response.json()["results"]
            resultados = [row for row in dados if corresponde(row, filtros)]
            if resultados:
                return f"🔍 {len(resultados)} resultado(s):\n\n" + "\n\n".join(formatar_os(r) for r in resultados)
            return "Nenhuma OS encontrada."
        else:
            return f"❌ Erro ao consultar OS ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na consulta: {e}"

def editar_os(criterios, novos_dados):
    print(f"[✏️] Buscando OS para editar com critérios: {criterios}")
    criterios = mapear_campos(criterios)
    novos_dados = mapear_campos(novos_dados)
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            rows = response.json()["results"]
            for row in rows:
                if corresponde(row, criterios):
                    row_id = row["id"]
                    update_response = requests.patch(f"{BASE_URL}{row_id}/", headers=HEADERS, json=novos_dados)
                    if update_response.status_code == 200:
                        return "✏️ OS atualizada com sucesso."
                    else:
                        return f"❌ Erro ao atualizar: {update_response.status_code} - {update_response.text}"
            return "OS não encontrada para edição."
        else:
            return f"❌ Erro na busca ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na edição: {e}"

def excluir_os(criterios):
    print(f"[🗑️] Buscando OS para exclusão com critérios: {criterios}")
    criterios = mapear_campos(criterios)
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            rows = response.json()["results"]
            for row in rows:
                if corresponde(row, criterios):
                    row_id = row["id"]
                    delete_response = requests.delete(f"{BASE_URL}{row_id}/", headers=HEADERS)
                    if delete_response.status_code == 204:
                        return "🗑️ OS excluída com sucesso."
                    else:
                        return f"❌ Erro ao excluir: {delete_response.status_code} - {delete_response.text}"
            return "OS não encontrada para exclusão."
        else:
            return f"❌ Erro ao buscar OS ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na exclusão: {e}"


@tool("Executar ação no Baserow")
def executar_acao(json_resultado: dict) -> str:
    """
    Executa uma ação no Baserow com base em um JSON estruturado contendo a chave 'acao'.
    Pode registrar, consultar, editar ou excluir OSs conforme o conteúdo da requisição.
    """
    if not isinstance(json_resultado, dict):
        return "❌ Erro: JSON inválido recebido."
    acao = json_resultado.get("acao", "").lower()
    if acao == "registrar":
        dados = json_resultado.get("dados", {})
        if not dados:
            return "❌ Erro: Dados ausentes para registro de OS."
        return registrar_os(dados)
    elif acao == "consultar":
        filtros = json_resultado.get("filtros", {})
        if not filtros:
            return "❌ Erro: Filtros ausentes para consulta."
        return consultar_os(filtros)
    elif acao == "editar":
        criterios = json_resultado.get("criterios", {})
        novos_dados = json_resultado.get("novos_dados", {})
        if not criterios or not novos_dados:
            return "❌ Erro: Critérios ou dados ausentes para edição."
        return editar_os(criterios, novos_dados)
    elif acao == "excluir":
        criterios = json_resultado.get("criterios", {})
        if not criterios:
            return "❌ Erro: Critérios ausentes para exclusão."
        return excluir_os(criterios)
    else:
        return "❌ Ação inválida ou não suportada."






