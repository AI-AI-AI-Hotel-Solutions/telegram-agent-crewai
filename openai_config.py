import os
import openai

def setup_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY") or "SUA_CHAVE_OPENAI"

def normalizar_formato(texto: str) -> str:
    prompt = f"""
Você é um assistente que reescreve pedidos de ordens de serviço para um formato padronizado.

Formato ideal:
"Registrar uma nova OS de [tipo de serviço] para o hóspede [nome ou nomes], no quarto [número], no dia [data] às [horário]. Os detalhes são: [detalhes do pedido]. Ele é [prioridade opcional]."

Reescreva a seguinte mensagem de entrada para esse formato. Se faltar alguma informação, use '---'.

Mensagem original:
{texto}

Reescrita:
"""

    resposta = openai.ChatCompletion.create(
        model="gpt-4",  # ou "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "Você reescreve pedidos de forma padronizada."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return resposta['choices'][0]['message']['content'].strip()
