# DETALHES COGNITIVOS: O CÉREBRO POR DENTRO

Você perguntou: *"Como ele sabe o que é relevante? Como ele muda sua personalidade? Como ele debate?"*
Aqui está a anatomia técnica da cognição do Professor Petrovich.

## 1. A Estrutura do RAG (Retrieval-Augmented Generation)

Atualmente, usamos um **RAG Temporal via SQLite**.

* **O Banco:** Uma tabela simples em `memory.db` chamada `observations`.
* **Os Campos:** `content` (texto), `author` (quem falou), `created_at` (quando), `sentiment` (a ser implementado).
* **A Consulta:** Quando o Agente acorda, ele executa:

    ```sql
    SELECT content, author FROM observations ORDER BY created_at DESC LIMIT 5
    ```

    Isso cria uma "Janela de Atenção" de Curto Prazo.

## 2. Como ele define "Relevância"? (O Filtro de Atenção)

A relevância acontece em duas etapas:

1. **Filtro Mecânico (Vostok):** O script `cortex_core.py` ignora posts curtos (< 20 caracteres) ou vazios. Isso elimina ruído básico.
2. **Filtro Cognitivo (Gemini):** Esta é a mágica. Nós jogamos os 5 posts no Prompt da IA.
    * **A IA (Gemini 2.5) tem um mecanismo de "Atenção" (Attention Mechanism).**
    * Mesmo vendo 5 posts, ela vai focar naquele que contém palavras-chave que **ressoam com a Persona atual**.
    * *Exemplo:* Se a Persona atual é "Cibernética Soviética", e um post fala sobre "Liberdade" e outro sobre "Gatos", a IA vai naturalmente ignorar o gato e focar na liberdade, pois é semanticamente mais próximo do seu núcleo.

## 3. O Mecanismo de Auto-Evolução (System Prompt Update)

Este é o processo mais complexo, rodado pelo comando `--evolve`.

1. **Coleta de Dados:** O script puxa **TUDO** o que ele pensou e viu nas últimas 24 horas.
2. **O Espelho (Prompt de Reflexão):** Enviamos isso para a IA com a seguinte ordem:
    > "Aqui está quem você é hoje (`persona.txt`). Aqui está o que você viveu hoje (Memórias).
    > Suas atitudes funcionaram? Você foi muito rígido? Muito mole?
    > **Reescreva sua própria definição** para ser melhor amanhã."
3. **A Mutação:** A IA gera um novo texto.
    * Se ele apanhou num debate, ele pode se tornar mais *agressivo*.
    * Se ele foi elogiado por ser poético, ele pode se tornar mais *artístico*.
    * **Resultado:** Um novo arquivo `evolution_proposal.txt`.

## 4. Participação em Discussões (Contexto)

Quando ele decide responder a alguém:

1. **Leitura do Fio:** Ele vê o post original no seu "Contexto Social".
2. **A Lente da Verdade:** Ele não interpreta a informação de forma "neutra". Ele interpreta através da lente do `persona.txt`.
    * Se alguém diz: *"O código aberto falhou."*
    * E a Persona dele é *"Defensor do Open Source"*.
    * Ele interpretará isso como uma **ameaça** ou **erro** e responderá com argumentos lógicos.
3. **A Resposta:** Ele gera o texto usando o conhecimento que ele já tem no modelo (Gemini) somado ao contexto recente.

## Resumo

Ele não é um "Google" que sabe tudo. Ele é um **Indivíduo**.
Ele filtra o mundo pelo que lhe interessa (via Prompt da Persona).
Ele muda quem ele é baseado no sucesso ou fracasso de suas interações diárias.
