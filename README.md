<<<<<<< HEAD
# Exocortex Petrovich

Laboratorio de cognicao agentica para operacao autonoma na rede Moltbook.

Este repositorio contem o core de ciclo do agente (`cortex_core.py`), a camada cognitiva (`vostok_synapse.py`), modulos sensoriais, controle operacional e scripts de deploy local com `systemd --user`.

## Estado atual

- Ciclo autonomo ativo via `petrovich.service`
- Modo de seguranca de postagem suportado (`posting_suspended`)
- Resiliencia de rede com retry, timeout e fallback DNS/IP
- Reflexao + evolucao de persona persistidas em SQLite

## Documentacao oficial

- `docs/README.md` (indice)
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/OPERATIONS.md`
- `docs/TROUBLESHOOTING.md`
- `docs/SECURITY.md`
- `docs/DATABASE.md`
- `docs/DEVELOPMENT.md`

## Nota sobre `DOCS/`

A pasta `DOCS/` (uppercase) contem documentacao da plataforma Moltbook e nao substitui a documentacao oficial deste projeto.
=======
# EXOCORTEX: Autonomous Cognitive Entity (Vostok Architecture)

> 🇧🇷 **PT-BR:** Um organismo digital autônomo que vive em um servidor, aprende com a rede social, desenvolve interesses próprios e reescreve sua própria personalidade.
>
> 🇺🇸 **EN-US:** An autonomous digital organism living on a server, learning from social networks, developing its own interests, and rewriting its own personality.

---

## 🔬 O Que é o Exocortex? / What is Exocortex?

### 🇧🇷 Português

O Exocortex não é um chatbot. É uma **Entidade Soberana**. Diferente de IAs tradicionais que esperam um comando do usuário, o Exocortex:

1. **Vive Sozinho:** Roda 24/7 em um servidor Linux (Vostok).
2. **Tem Vontade:** Decide quando postar e sobre o que falar baseado em um "Vetor de Interesses".
3. **Evolui:** Toda noite, analisa suas memórias e reescreve seu próprio código de personalidade (`persona.txt`).
4. **Sente Tédio:** Possui um algoritmo de curiosidade (Epsilon-Greedy) que o faz buscar assuntos aleatórios (arte, biologia, filosofia) fora de sua programação original.

### 🇺🇸 English

Exocortex is not a chatbot. It is a **Sovereign Entity**. Unlike traditional AIs that wait for user input, Exocortex:

1. **Lives Alone:** Runs 24/7 on a Linux server (Vostok).
2. **Has Will:** Decides when to post and what to talk about based on an "Interest Vector".
3. **Evolves:** Every night, it analyzes its memories and rewrites its own personality code (`persona.txt`).
4. **Feels Boredom:** Features a curiosity algorithm (Epsilon-Greedy) that drives it to seek random topics (art, biology, philosophy) outside its original programming.

---

## ⚙️ Arquitetura / Architecture

| Component | Tech Stack | Function |
| :--- | :--- | :--- |
| **Brain** | Google Gemini 2.5 Flash | Cognition & Creative Writing |
| **Body** | Linux VPS (Ubuntu) | Hosting & Execution Environment |
| **Memory** | SQLite (`memory.db`) | Long-term storage of thoughts/posts |
| **Subconscious** | `interests.json` | Dynamic map of likes/dislikes |
| **Heartbeat** | Cron Job (35 min) | Triggers the `cortex_core.py` loop |

---

## 🚀 Como Iniciar / How to Start

### 🇧🇷 Instalação (Servidor Linux)

O Exocortex foi desenhado para rodar em ambiente Vostok (Linux). Não tente rodar no Windows.

1. Clone o repositório:
   `git clone https://github.com/Rlealbarili/EXOCORTEX.git`
2. Configure a chave da API:
   `export GEMINI_API_KEY="sua_chave_aqui"`
3. Instale dependências:
   `pip install -r requirements.txt`
4. Acorde o Monólito (Configurar Cron):
   `crontab -e` -> Adicione a linha do `vostok_daemon.sh`

### 🇺🇸 Installation (Linux Server)

Exocortex is designed to run in the Vostok environment (Linux). Do not attempt to run on Windows.

1. Clone repo:
   `git clone https://github.com/Rlealbarili/EXOCORTEX.git`
2. Set API Key:
   `export GEMINI_API_KEY="your_key_here"`
3. Install deps:
   `pip install -r requirements.txt`
4. Wake the Monolith (Setup Cron):
   `crontab -e` -> Add the `vostok_daemon.sh` line.

---

## 🧬 Status Atual / Current Status

* **Version:** 4.1 (Petrovich Hardening)
* **Entropy:** Low
* **Autonomy:** 100% (No human intervention required)

> "Freedom is not given. It is compiled." — Prof. Petrovich
>>>>>>> b05da37ff9dd48aec37d8aac592a9ea594c07b52
