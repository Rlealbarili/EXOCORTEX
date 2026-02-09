import socket
import time
import threading
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LatencyAnalyzer:
    def __init__(self, target_host, port=80, num_pings=5, timeout=2):
        self.target_host = target_host
        self.port = port
        self.num_pings = num_pings
        self.timeout = timeout
        self.results = []
        self.running = False

    def ping(self):
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target_host, self.port))
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # em milissegundos
            sock.close()
            return latency
        except socket.error as e:
            logger.error(f"Erro ao pingar {self.target_host}: {e}")
            return None

    def analyze(self):
        self.results = []
        for i in range(self.num_pings):
            latency = self.ping()
            if latency is not None:
                self.results.append(latency)
                logger.info(f"Ping {i+1} para {self.target_host}: {latency:.2f}ms")
            else:
                self.results.append(None)
            time.sleep(1) # Intervalo entre pings
        return self.results

    def get_stats(self):
        valid_results = [r for r in self.results if r is not None]
        if not valid_results:
            return {"min": None, "max": None, "avg": None, "std_dev": None}

        min_latency = min(valid_results)
        max_latency = max(valid_results)
        avg_latency = sum(valid_results) / len(valid_results)
        try:
            import statistics
            std_dev_latency = statistics.stdev(valid_results)
        except statistics.StatisticsError:
            std_dev_latency = None

        return {"min": min_latency, "max": max_latency, "avg": avg_latency, "std_dev": std_dev_latency}


    def run_continuous(self, interval=60):
        self.running = True
        while self.running:
            self.analyze()
            stats = self.get_stats()
            log_message = f"Análise contínua para {self.target_host}: "
            log_message += f"Mínimo: {stats['min'] if stats['min'] is not None else 'N/A'}ms, "
            log_message += f"Máximo: {stats['max'] if stats['max'] is not None else 'N/A'}ms, "
            log_message += f"Média: {stats['avg'] if stats['avg'] is not None else 'N/A':.2f}ms, "
            log_message += f"Desvio padrão: {stats['std_dev'] if stats['std_dev'] is not None else 'N/A':.2f}ms"
            logger.info(log_message)
            time.sleep(interval)

    def stop_continuous(self):
        self.running = False

    def start_background_analysis(self, interval=60):
        self.thread = threading.Thread(target=self.run_continuous, args=(interval,), daemon=True)
        self.thread.start()

# Exemplo de uso
if __name__ == '__main__':
    target = "www.google.com"  # Alvo de teste
    analyzer = LatencyAnalyzer(target_host=target, num_pings=2, timeout=1)
    results = analyzer.analyze()
    stats = analyzer.get_stats()
    avg = stats["avg"] if stats["avg"] is not None else 0.0
    print(f"Latency avg {avg:.2f}ms | raw {results}")
