import datetime
import requests
from crewai.tools import tool
import re

# Token e base do Baserow
API_TOKEN = "XqIY4Ru5ELx2ifWKyFGfJVt0HPfEyyAP"
TABLE_ID = "589034"
BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# Mapeamento dos campos legíveis para os field_xxx do Baserow
FIELD_MAP = {
    "Data/Hora": "field_4761397",
    "E-mail Autor": "field_4761405",
    "Nome do Hóspede": "field_4761406",
    "Quarto": "field_4761407",
    "Data do Serviço": "field_4761412",
    "Horário do Serviço": "field_4761414",
    "Tipo de Serviço": "field_4761415",
    "Detalhes do Pedido": "field_4761417",
    "Prioridade": "field_4761418",
    "Departamentos": "field_4820649"
}

# IDs dos departamentos
DEPARTAMENTOS = {
    "Concierge": 3657472,
    "Recepção": 3657473,
    "Bar": 3657474,
    "Salão": 3657475,
    "Cozinha": 3657476,
    "Governança": 3657477
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
        "normal": 3616249,
        "urgente": 3616250,
        "atenção": 3616251,
        "vip": 3616251,
        "cliente vip": 3616251,
        "cliente habitue": 3641220,
        "cliente habitual": 3641220
    }
    return mapa.get(texto, 3616249)

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
    prioridade = os.get('field_4761418', {}).get('value', 'Normal')
    detalhes = os.get('field_4761417', '')
    data_servico = os.get('field_4761412', '---')
    criado_em = os.get('field_4761397', '')

    try:
        criado_dt = datetime.datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
        criado_formatado = f"{criado_dt.date()} às {criado_dt.strftime('%H:%M')}"
    except:
        criado_formatado = criado_em

    return f"""
- Quarto: {os.get('field_4761407', '---')}
- Data do Serviço: {data_servico}
- Horário: {os.get('field_4761414', '---')}
- Tipo de Serviço: {os.get('field_4761415', '---')}
- Detalhes do Pedido: {detalhes}
- Prioridade: {prioridade}
- Autor: {os.get('field_4761405', '---')}
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


def corresponde(row, filtros):
    for k, v in filtros.items():
        valor_row = row.get(k)
        if valor_row is None:
            return False
        if isinstance(valor_row, dict):
            valor_row = valor_row.get("value", "")
        if isinstance(v, dict):
            v = v.get("value", v)
        if str(valor_row).strip().lower() != str(v).strip().lower():
            return False
    return True


def consultar_os(filtros):
    filtros = mapear_campos(filtros)
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        if response.status_code == 200:
            dados = response.json()["results"]
            resultados = []
            for row in dados:
                if corresponde(row, filtros):
                    resultados.append(row)
            return f"🔍 {len(resultados)} resultado(s):\n\n" + "\n\n".join(formatar_os(r) for r in resultados) if resultados else "Nenhuma OS encontrada."
        else:
            return f"❌ Erro ao consultar OS ({response.status_code})"
    except Exception as e:
        return f"❌ Erro na consulta: {e}"


def editar_os(criterios, novos_dados):
    criterios = mapear_campos(criterios)
    novos_dados = mapear_campos(novos_dados)
    print(f"[✏️] Buscando OS para editar com critérios: {criterios}")
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
    criterios = mapear_campos(criterios)
    print(f"[🧹] Tentando excluir com filtros: {criterios}")
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
                        return f"❌ Erro ao excluir: {delete_response.status_code}"
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



# coisas novas referente a agendamento


TELEGRAM_TOKEN = "7504265835:AAGkAEHaMmBW59SlfQ0ga9XuUF-lsx83zRU"  # Substitua pelo token do seu bot
GRUPOS_TELEGRAM = {
    "Concierge": -4853736293,
    "Recepção": -4962953534,
    "Bar": -4790526640,
    "Salão": -4951559297,
    "Cozinha": -4810278204,
    "Governança": -4957904992,
}


def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"📨 Status: {response.status_code} | Grupo: {chat_id}")
        print(response.text)
    except Exception as e:
        print(f"❌ Erro ao enviar para {chat_id}: {e}")

def formatar_os_item(os, idx):
    hospede = os.get(FIELD_MAP["Nome do Hóspede"], "---")
    quarto = os.get(FIELD_MAP["Quarto"], "---")
    prioridade = os.get(FIELD_MAP["Prioridade"], {}).get("value", "Normal")
    horario = os.get(FIELD_MAP["Horário do Serviço"], "---")
    servico = os.get(FIELD_MAP["Tipo de Serviço"], "---")
    detalhes = os.get(FIELD_MAP["Detalhes do Pedido"], "---")
    data_servico = os.get(FIELD_MAP["Data do Serviço"], "---")

    return f"""🔖 OS-{idx:03} - Hóspedes: {hospede} - SUÍTE UH {quarto}
  ⚡ {prioridade.upper()}
  📅 {data_servico}
  ⏰ {horario}
  🎯 Serviço: {servico}
  📝 Detalhes: {detalhes}"""

def enviar_relatorio_diario():
    hoje = datetime.date.today()
    fim = hoje + datetime.timedelta(days=7)

    print(f"[{datetime.datetime.now()}] 🚀 Início da geração do relatório")
    print(f"🗓️ Intervalo de busca: {hoje} até {fim}")

    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        print(f"🔍 Requisição ao Baserow retornou: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Erro ao buscar OS: {response.status_code}")
            return

        dados = response.json().get("results", [])
        print(f"📦 OS encontradas no total: {len(dados)}")

        grupos_mensagens = {nome: [] for nome in GRUPOS_TELEGRAM}
        data_hoje_fmt = hoje.strftime("%d/%m/%Y")

        for idx, os in enumerate(dados, 1):
            data_str = os.get(FIELD_MAP["Data do Serviço"])
            if not data_str:
                continue

            try:
                data_os = datetime.date.fromisoformat(data_str)
            except:
                continue

            if data_os < hoje or data_os > fim:
                print(f"ℹ️ OS-{idx:03} fora do intervalo, ignorada.")
                continue

            os_txt = formatar_os_item(os, idx)
            dia_fmt = data_os.strftime("%d/%m/%Y")

            if data_os == hoje:
                categoria = f"🔴 HOJE\n{os_txt}"
            elif data_os == hoje + datetime.timedelta(days=1):
                categoria = f"🟡 AMANHÃ\n{os_txt}"
            else:
                categoria = f"🟢 {dia_fmt}\n{os_txt}"

            deps = os.get(FIELD_MAP["Departamentos"], [])
            print(f"🧪 OS-{idx:03} Departamentos: {deps}")

            for dep in deps:
                dep_id = dep.get("id") if isinstance(dep, dict) else dep
                nome_dep = next((k for k, v in DEPARTAMENTOS.items() if v == dep_id), None)
                if nome_dep:
                    grupos_mensagens[nome_dep].append(categoria)

        total_enviados = 0
        for nome_dep, mensagens in grupos_mensagens.items():
            corpo = f"📋 OS DOS PRÓXIMOS 7 DIAS - {data_hoje_fmt}\n\n"
            corpo += "\n\n".join(mensagens) if mensagens else "✅ Nenhuma OS nos próximos 7 dias."

            chat_id = GRUPOS_TELEGRAM[nome_dep]
            print(f"📨 Enviando para {nome_dep} ({chat_id})...")
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": corpo, "parse_mode": "Markdown"}
            )
            print(f"📨 Status: {r.status_code} | Grupo: {chat_id}")
            print(r.text)
            if r.status_code == 200:
                total_enviados += 1

        return f"✅ Mensagens enviadas para {total_enviados} departamentos."

    except Exception as e:
        print(f"🔥 Exceção inesperada ao gerar o relatório:\n{e}")



