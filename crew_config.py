from crewai import Crew, Agent, Task
from sheet_handler import executar_acao
from openai_config import setup_openai

setup_openai()

comandante = Agent(
    role="Comandante de OS",
    goal="Interpretar comandos em linguagem natural e converter em ações estruturadas de OS",
    backstory="Agente inteligente que entende pedidos de gestores e identifica se é para registrar, consultar, editar ou excluir uma ordem de serviço.",
    verbose=True
)

executor = Agent(
    role="Executor de OS",
    goal="Executar ações diretamente na planilha Google com base em instruções",
    backstory="Responsável por registrar, consultar, editar ou excluir OS conforme os dados extraídos pelo Comandante.",
    verbose=True
)

task_comando = Task(
    description="Analise o texto recebido, identifique a ação desejada (registrar, consultar, editar, excluir) e retorne um JSON estruturado com os dados necessários para executar essa ação.",
    expected_output="Um JSON com o campo 'acao' e os dados correspondentes à operação solicitada.",
    agent=comandante
)

task_execucao = Task(
    description="Receba o JSON retornado e execute a operação solicitada (registro, consulta, edição ou exclusão) na planilha.",
    expected_output="Mensagem confirmando a ação ou listando resultados.",
    agent=executor
)

crew = Crew(
    agents=[comandante, executor],
    tasks=[task_comando, task_execucao],
    process="sequential"
)

def process_message(text):
    resultado = crew.kickoff(inputs={"input": text})
    return resultado if isinstance(resultado, str) else str(resultado)

