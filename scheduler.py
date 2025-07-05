from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from baserow_handler import enviar_relatorio_diario
import time

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

    scheduler.add_job(
        enviar_relatorio_diario,
        trigger="cron",
        hour=2,
        minute=15,
        id="relatorio_diario",
        name="Enviar relatório diário às 02:15"
    )

    scheduler.start()
    print(f"[{datetime.now()}] ⏰ Agendador iniciado - relatório diário será enviado às 02:15")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
