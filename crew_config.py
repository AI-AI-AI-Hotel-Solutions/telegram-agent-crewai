from crewai import Crew, Agent, Task
from baserow_handler import executar_acao
from openai_config import setup_openai
import json

setup_openai()

# Agente responsável por interpretar linguagem natural
comandante = Agent(
    role="Comandante de OS",
    goal="Interpretar comandos em linguagem natural e converter em ações estruturadas de OS",
    backstory="Agente inteligente que entende pedidos de gestores e identifica se é para registrar, consultar, editar ou excluir uma ordem de serviço.",
    verbose=True
)

# Agente executor que realiza a ação na base Baserow
executor = Agent(
    role="Executor de OS",
    goal="Executar ações diretamente na base Baserow com base em instruções",
    backstory="Responsável por registrar, consultar, editar ou excluir OS conforme os dados extraídos pelo Comandante.",
    verbose=True,
    tools=[executar_acao]
)


# Tarefa 1: interpretar linguagem natural
task_comando = Task(
    description="""
Você é um agente especializado em interpretar comandos de gestores para gerar ordens de serviço.

Dado um texto em linguagem natural, identifique qual das seguintes ações ele descreve:
- "registrar": inserir uma nova OS na planilha
- "consultar": buscar dados existentes
- "editar": modificar uma OS existente
- "excluir": apagar uma OS existente

Sua tarefa é retornar um JSON estruturado com:
- Campo 'acao' (registrar, consultar, editar, excluir)
- Campo correspondente aos dados da ação.

🎯 Exemplos:
---
Entrada:
"Registrar jantar romântico para o hóspede Rodrigo, quarto 12, dia 28 de junho, às 22h. Entrada e prato principal."

Saída:
{
  "acao": "registrar",
  "dados": {
    "Nome do Hóspede": "Rodrigo",
    "Quarto": "12",
    "Data do Serviço": "2025-06-28",
    "Horário do Serviço": "22:00",
    "Tipo de Serviço": "Jantar romântico",
    "Detalhes do Pedido": "Entrada e prato principal",
    "Prioridade": "Normal"
  }
}

---
Entrada:
"Excluir o registro do hóspede João no quarto 5 com serviço de café da manhã"

Saída:
{
  "acao": "excluir",
  "criterios": {
    "Nome do Hóspede": "João",
    "Quarto": "5",
    "Tipo de Serviço": "Café da manhã"
  }
}

---
Agora processe a seguinte mensagem:
{input}
""",
    expected_output="Um JSON no formato especificado contendo a ação e os dados.",
    agent=comandante
)

# Task 2 — execução no Baserow
task_execucao = Task(
    description="Execute a ação na base Baserow com base no JSON fornecido, usando a função executar_acao.",
    expected_output="Mensagem confirmando a ação ou listando resultados.",
    agent=executor,
    function=executar_acao,
    input_key="output"  # Isso é a saída da task anterior (task_comando)
)

# Orquestração sequencial
crew = Crew(
    agents=[comandante, executor],
    tasks=[task_comando, task_execucao],
    process="sequential"
)

# Função principal chamada pelo webhook
def process_message(text):
    try:
        resultado = crew.kickoff(inputs={"input": text})
        return resultado if isinstance(resultado, str) else str(resultado)
    except Exception as e:
        return f"[Erro interno]\n{type(e).__name__}: {e}"


