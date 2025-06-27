import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

PLANILHA_ID = "1rJT7v40X5V4dcW4AUplxIPI8vDR9yBBnkTG8PoC4QFg"
ABA = "OS"
EMAIL_AUTOR = "sined.marecas@gmail.com"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(PLANILHA_ID).worksheet(ABA)

def executar_acao(json_resultado):
    if not isinstance(json_resultado, dict) or "acao" not in json_resultado:
        return "Ação inválida ou não reconhecida."

    acao = json_resultado["acao"]
    if acao == "registrar":
        return registrar_os(json_resultado.get("dados", {}))
    elif acao == "consultar":
        return consultar_os(json_resultado.get("filtros", {}))
    elif acao == "editar":
        return editar_os(json_resultado.get("criterios", {}), json_resultado.get("novos_dados", {}))
    elif acao == "excluir":
        return excluir_os(json_resultado.get("criterios", {}))
    else:
        return "Ação não suportada."

def registrar_os(dados):
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = [
        agora,
        EMAIL_AUTOR,
        dados.get("Nome do Hóspede", ""),
        dados.get("Quarto", ""),
        dados.get("Data do Serviço", ""),
        dados.get("Horário do Serviço", ""),
        dados.get("Tipo de Serviço", ""),
        dados.get("Detalhes do Pedido", ""),
        dados.get("Prioridade", ""),
    ]
    sheet.append_row(linha)
    return "✅ OS registrada com sucesso."

def consultar_os(filtros):
    registros = sheet.get_all_records()
    resultados = []
    for row in registros:
        match = all(str(row.get(k, "")).lower() == str(v).lower() for k, v in filtros.items())
        if match:
            resultados.append(row)
    return f"🔍 {len(resultados)} resultado(s) encontrado(s):\n" + "\n".join(str(r) for r in resultados) if resultados else "Nenhuma OS encontrada."

def editar_os(criterios, novos_dados):
    registros = sheet.get_all_records()
    for i, row in enumerate(registros):
        match = all(str(row.get(k, "")).lower() == str(v).lower() for k, v in criterios.items())
        if match:
            for key, value in novos_dados.items():
                col = sheet.find(key).col
                sheet.update_cell(i+2, col, value)
            return "✏️ OS atualizada com sucesso."
    return "OS não encontrada para edição."

def excluir_os(criterios):
    registros = sheet.get_all_records()
    for i, row in enumerate(registros):
        match = all(str(row.get(k, "")).lower() == str(v).lower() for k, v in criterios.items())
        if match:
            sheet.delete_row(i+2)
            return "🗑️ OS excluída com sucesso."
    return "OS não encontrada para exclusão."
