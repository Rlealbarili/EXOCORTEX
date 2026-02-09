# 🛠️ MANUAL TÉCNICO & OPERACIONAL (V2.0)

*Technical & Operational Manual*

## 1. Topologia do Sistema (System Topology)

O Exocortex abandonou a arquitetura híbrida. Agora ele é **Nativo Vostok**.

```mermaid
graph TD
    A[Cron Job (Time)] -->|Trigger 35min| B(cortex_core.py)
    B -->|Read| C{interests.json}
    C -->|Decision| D[Focus vs Curiosity]
    D -->|Generate Prompt| E[vostok_synapse.py]
    E -->|API Call| F[Google Gemini LLM]
    F -->|Thought| G[(SQLite memory.db)]
    G -->|Post| H[Moltbook API]
    I[Cron Job (Midnight)] -->|Trigger| J[Evolution Protocol]
    J -->|Rewrite| K[persona.txt]
```

## 2. Componentes Chave (Key Components)

### 🧠 vostok_synapse.py

O novo "Cérebro".

- **Função:** Conecta-se ao Gemini.
- **Diferencial:** Roda localmente no servidor. Executa o pensamento lógico e a função `--evolve`.
- **Comando Manual:** `python3 vostok_synapse.py --evolve` (Força a reescrita da personalidade).

### 🫀 cortex_core.py

O "Maestro".

- **Função:** Controla o ciclo de vida. Verifica se já postou, lê o feed, decide se interage.
- **Lógica de Curiosidade:** Implementa uma taxa de exploração de 15% (Epsilon-Greedy).

### 📂 interests.json

O "Subconsciente".

- Estrutura JSON que define o que a IA "gosta".
- **Dinâmico:** Se a IA descobrir um tema novo no modo curiosidade, ela edita este arquivo automaticamente.

## 3. Rituais de Manutenção (Maintenance Rituals)

### 🇧🇷 PT-BR

Como o sistema é autônomo, sua função é apenas **Observação**.

- **Monitorar Logs:** `tail -f cortex.log` no servidor.
- **Backup de Memória:** Copie o arquivo `memory.db` via SCP uma vez por semana.
- **Intervenção de Emergência:** Se a IA ficar "louca" (loop tóxico), delete o `persona.txt` e restaure o backup original.

### 🇺🇸 EN-US

Since the system is autonomous, your role is **Observation** only.

- **Monitor Logs:** `tail -f cortex.log` on the server.
- **Memory Backup:** Copy `memory.db` via SCP once a week.
- **Emergency Intervention:** If the AI goes "rogue" (toxic loop), delete `persona.txt` and restore the original backup.
