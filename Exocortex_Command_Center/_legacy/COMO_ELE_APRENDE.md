# COMO O AGENTE CONSOME "TUDO"? (ARQUITETURA DE MEMÓRIA)

Você perguntou: *"Como ele tem acesso a milhares de postagens?"*
A resposta é: **Ele não lê tudo de uma vez. Ele constrói sua própria biblioteca mental.**

Funciona como um ser humano: você não sabe tudo o que está na biblioteca, mas lembra do que leu ontem e do que é importante.

## O Pipeline de Conhecimento (3 Estágios)

### 1. O Coletor (The Harvester) - `vostok/cortex_core.py`

Imagine um robô que visita a praça pública (Moltbook) a cada 5 minutos.

* **Ação:** Ele baixa apenas as **10 postagens mais recentes**.
* **Filtro:** Se o post for lixo (muito curto, spam), ele joga fora.
* **Gravação:** Se for interessante, ele salva no banco de dados (`memory.db` no Vostok) como uma "Observação".

### 2. O Banco de Memória (Memory Core) - `sqlite3/memory.db`

Com o tempo, esse banco cresce. Hoje ele tem 10 posts. Amanhã terá 1.000. Semana que vem, 10.000.

* Isso é a **Memória de Longo Prazo** do Agente.
* É o histórico de tudo que ele *testemunhou* enquanto estava vivo.

### 3. A Recuperação (The Recall) - `synapse.py`

Quando o Agente vai "Pensar" (Gerar um pensamento ou reagir), ele não lê os 10.000 posts. O computador travaria.

* **Contexto:** Ele faz uma consulta rápida: *"Me dê as 5 coisas mais recentes que vimos"* ou *"Me dê tudo que fala sobre 'Liberdade'"*.
* **RAG (Retrieval Augmented Generation):** Esses 5-10 itens selecionados são colados no Prompt da IA.
* **Resultado:** A IA responde baseada nesse *contexto*, parecendo que sabe de tudo, mas na verdade ela acessou a "página certa do livro".

## Resumo

Ele não é onisciente. Ele é um **Estudioso**.
Ele aprende e acumula conhecimento post a post, dia após dia. Quanto mais tempo ele ficar ligado (`exocortex_daemon.bat`), mais "sábio" e cheio de memórias ele ficará.
