import psutil
import logging
import time

# Configuração de Logging
logging.basicConfig(filename='recursos_gerenciador.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecursosGerenciador:
    def __init__(self, intervalo_monitoramento=5):
        self.intervalo_monitoramento = intervalo_monitoramento

    def monitorar_recursos(self):
        """
        Monitora o uso de CPU, memória e disco.
        """
        try:
            while True:
                cpu_percent = psutil.cpu_percent(interval=self.intervalo_monitoramento)
                mem_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent

                logger.info(f"CPU: {cpu_percent}%, Memória: {mem_percent}%, Disco: {disk_percent}%")

                if cpu_percent > 80:
                    logger.warning("Uso de CPU alto! Possíveis gargalos.")
                if mem_percent > 90:
                    logger.warning("Uso de memória alto! Considere otimizar ou aumentar a memória.")
                if disk_percent > 90:
                    logger.warning("Uso de disco alto! Libere espaço ou otimize o armazenamento.")
        except KeyboardInterrupt:
            logger.info("Monitoramento de recursos encerrado.")
        except Exception as e:
            logger.error(f"Erro no monitoramento de recursos: {e}")

    def snapshot(self):
        """
        Coleta uma leitura única de recursos para uso no ciclo sensorial.
        """
        cpu_percent = psutil.cpu_percent(interval=0.2)
        mem_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        logger.info(f"Snapshot - CPU: {cpu_percent}%, Memória: {mem_percent}%, Disco: {disk_percent}%")
        return cpu_percent, mem_percent, disk_percent

if __name__ == "__main__":
    gerenciador = RecursosGerenciador()
    cpu, mem, disk = gerenciador.snapshot()
    print(f"CPU {cpu:.1f}% | MEM {mem:.1f}% | DISK {disk:.1f}%")
