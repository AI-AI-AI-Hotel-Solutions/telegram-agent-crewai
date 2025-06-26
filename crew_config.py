from crewai import Crew, Agent, Task
from openai_config import setup_openai

setup_openai()

agent = Agent(
    role="Concierge Virtual",
    goal="Ajudar com solicitações de hotelaria e registrar ordens de serviço",
    backstory="Agente especialista em atendimento e operações internas de hotel",
    verbose=True
)

task = Task(
    description="Interpretar a solicitação e redigir uma resposta profissional",
    expected_output="Resposta clara, objetiva e útil para o hóspede",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    process= "sequential"  # Adicione esse parâmetro!
)

def process_message(text):
    result = crew.kickoff(inputs={"input": text})
    return result if isinstance(result, str) else str(result)
