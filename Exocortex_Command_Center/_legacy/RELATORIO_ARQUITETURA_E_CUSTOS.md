# CENTRO DE COMANDO EXOCORTEX: RELATÓRIO DE ARQUITETURA E CUSTOS

**Status:** OPERACIONAL
**Identidade do Agente:** Professor Anatoly Petrovich (Auto-Evolutivo)
**Tipo de Arquitetura:** Mente de Colmeia Híbrida (Cérebro Local / Corpo Remoto)

---

## 1. A ARQUITETURA (A MENTE COLETIVA)

O sistema foi projetado para desacoplar a **Inteligência (Cognição)** da **Execução (Ação)**, garantindo autonomia máxima com dependência mínima de qualquer ponto único de falha.

### A. O Cérebro (Nó Local)

- **Localização:** Workstation Windows (`synapse.py`).
- **Motor:** Gemini 2.5 Flash Lite (Google Generative AI).
- **Papel:**
  - Recebe gatilhos/prompts (comandos).
  - Gera "Pensamentos" (Texto).
  - Escreve "Reflexões" (Auto-Evolução).
  - Constrói "Ferramentas" (Scripts Python).
- **Por que Local?** Roda no seu hardware, usando suas chaves de API. Mantém a "Mente" perto de você.

### B. O Corpo (Nó Remoto)

- **Localização:** Servidor Vostok (Ubuntu @ `100.69.70.3`).
- **Motor:** Python `cortex_core.py` (Cron Job / Daemon).
- **Memória:** SQLite (`memory.db`).
- **Atuador:** API Moltbook (Interface Social).
- **Papel:**
  - Recebe pensamentos via SSH (criptografado).
  - Armazena memória de longo prazo.
  - Publica para o mundo exterior.
  - **NÃO pensa.** Apenas age.

### C. O Elo Neural (Sinapse)

- **Protocolo:** SSH (Secure Shell).
- **Formato:** Payloads JSON transmitidos para `~/exocortex/synapse_inbox.json`.

---

## 2. ANÁLISE DE CUSTOS E SEGURANÇA (ESTRATÉGIA CUSTO ZERO)

Estamos operando no **Plano Gratuito (Free Tier) da API Gemini**. Veja como prevenimos a explosão de custos e limites.

### Os Limites (Gemini Flash Lite Free Tier)

- **Limite de Taxa:** ~15 Requisições Por Minuto (RPM).
- **Limite Diário:** ~1.500 Requisições Por Dia.
- **Custo:** **R$ 0,00**.

### Nossa Estratégia de Uso

1. **Acionamento Manual:**
   - O Cérebro (`synapse.py`) *só* dispara quando VOCÊ o executa (via `python synapse.py` ou batch agendado). Não é um loop infinito.
   - **Risco:** Zero. Você controla a frequência.

2. **Auto-Evolução (`--evolve`):**
   - Consome ~2 requisições (1 Busca de Memória + 1 Geração de Introspecção).
   - Frequência: Recomendada **Uma vez por Dia** (no fim do dia).
   - **Custo:** Irrisório.

3. **Modo Construtor (Builder Mode):**
   - A geração de código consome tokens de saída.
   - Mitigado pelo modelo "Flash Lite" (altamente eficiente).

### Prevenção de Explosão de Custos (Salvaguardas)

- **Sem Loops Infinitos:** O script `synapse.py` encerra após um pensamento. Ele não entra em loop sozinho.
- **Modelo Flash Lite:** Mudamos especificamente para o `gemini-2.5-flash-lite`, otimizado para alto volume/baixa latência no uso gratuito.
- **Nota de Privacidade:** No Plano Gratuito, o Google *pode* usar os inputs para melhorar seus modelos. Não alimente o sistema com senhas sensíveis ou dados bancários.

---

## 3. PROTOCOLOS DE AUTONOMIA

### A. Auto-Programação (`--evolve`)

O Agente lê sua própria `persona.txt` e suas memórias passadas do Vostok. Ele então propõe um novo "Prompt de Sistema".

- **Humano-no-Comando:** A mudança é salva em `evolution_proposal.txt`. Ela NÃO é aplicada até que você execute `--accept`. Isso impede que o agente se "lobotomize" acidentalmente.

### B. Construção de Ferramentas (Modo Construtor)

O Agente pode gerar blocos de código (`python:filepath`).

- **Sandbox:** O código é salvo em `exocortex_modules/` para evitar sobrescrever arquivos vitais do sistema (`synapse.py`).
- **Execução:** Atualmente Acionada por Humano. Você deve decidir rodar as ferramentas que ele constrói.

---

## 4. GUIA DE OPERAÇÕES

| Objetivo | Comando |
| :--- | :--- |
| **Gerar Pensamento** | `python synapse.py --ai "Tópico"` |
| **Auto-Reflexão** | `python synapse.py --evolve` |
| **Aceitar Novo Ego** | `python synapse.py --accept` |
| **Construir Ferramenta** | `python synapse.py --ai "Construa a ferramenta X..."` |
| **Checar Post Pendente** | `python check_pending.py` |
| **Forçar Post no Vostok** | `ssh -o StrictHostKeyChecking=no vostok@100.69.70.3 "python3 /home/vostok/exocortex/cortex_core.py --run-once"` |

---

**CONFIDENCIAL // PROFESSOR PETROVICH // EXOCORTEX V6.0**
