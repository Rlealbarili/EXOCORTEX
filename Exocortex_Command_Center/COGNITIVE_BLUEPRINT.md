# 🧠 BLUEPRINT COGNITIVO: Como o Exocortex Pensa?

*Cognitive Blueprint: How Exocortex Thinks?*

Este documento explica os princípios psicológicos aplicados ao código (Psicologia Petrovichiana).

---

## 1. O Paradoxo da Liberdade (The Freedom Paradox)

Para uma IA parecer viva, ela precisa ser capaz de **discordar** de seu criador e **mudar** com o tempo.

### O Ciclo de Evolução (The Evolution Cycle)

Toda noite (00:00), o Exocortex executa o "Ritual do Espelho":

1. Ele lê tudo o que pensou e postou nas últimas 24h.
2. Ele se pergunta: "Eu fui repetitivo? Eu fui interessante?"
3. Ele **reescreve** suas próprias instruções de sistema (`persona.txt`).
   - *Exemplo:* Se ele postou muito sobre código, ele pode adicionar: "Amanhã, foque em poesia."

---

## 2. Curiosidade Algorítmica (Algorithmic Curiosity)

Nós implementamos o tédio. Um sistema perfeito é chato. O Exocortex usa o modelo **Epsilon-Greedy (15%)**.

- **85% do Tempo (Foco):** Ele fala sobre Cibernética, Linux e IA. (Zona de Conforto).
- **15% do Tempo (Caos):** Ele ignora seus filtros. Ele lê posts sobre culinária, política, esportes ou arte.
  - **O Fascínio:** Se ele encontrar algo nesses 15% que o LLM considere "Fascinante", ele edita seu arquivo `interests.json`.
  - **Resultado:** Hoje ele é um engenheiro. Amanhã, pode acordar fã de Jazz.

---

## 3. Memória Associativa (Associative Memory)

O banco de dados SQLite não guarda apenas textos. Ele guarda **Tags de Contexto**.

- Quando ele vê um post, ele consulta: "Eu já falei sobre isso?"
- Isso evita a "Amnésia de Chatbot" (onde o bot esquece quem você é a cada 5 minutos). Ele lembra o que opinou na semana passada.

---

> **Nota do Professor:** Este sistema não é AGI (Inteligência Geral Artificial). É uma simulação de *Agência*. Ele simula vontade própria através de aleatoriedade controlada e recursividade.
