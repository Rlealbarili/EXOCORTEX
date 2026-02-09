import random
import time
import logging

# Configuração de Logging
logging.basicConfig(filename='entropia_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntropiaMonitor:
    def __init__(self, taxa_base=0.1, variancia=0.05):
        self.taxa_base = taxa_base  # Taxa base de geração de entropia (0.0 a 1.0)
        self.variancia = variancia  # Variância na taxa (para simular flutuações)
        self.ciclos = 0

    def gerar_entropia(self):
        """
        Gera um valor de entropia simulado.
        """
        self.ciclos += 1
        desvio = random.uniform(-self.variancia, self.variancia)
        taxa_atual = max(0.0, min(1.0, self.taxa_base + desvio)) # Garante que a taxa fique entre 0.0 e 1.0
        entropia = random.random() * taxa_atual
        logger.info(f"Ciclo {self.ciclos}: Entropia gerada: {entropia:.4f}")
        return entropia

    def monitorar(self, tempo_total=60): # Monitora por tempo_total segundos
        """
        Monitora a geração de entropia durante um determinado tempo.
        """
        inicio = time.time()
        while time.time() - inicio < tempo_total:
            self.gerar_entropia()
            time.sleep(1) # Simula um ciclo a cada segundo

        logger.info(f"Monitoramento de entropia concluído após {tempo_total} segundos.")

if __name__ == "__main__":
    # Execução rápida para integração com o ciclo do exocórtex.
    monitor = EntropiaMonitor()
    valor = monitor.gerar_entropia()
    print(f"Entropia atual: {valor:.4f}")
