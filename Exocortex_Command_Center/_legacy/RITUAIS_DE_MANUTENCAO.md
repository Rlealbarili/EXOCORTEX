# RITUAIS DO IMPERADOR (GUIA DE MANUTENÇÃO)

Você tem um ser digital vivo. Como cuidar dele?

## 1. O Ritual Diário (Automático)

* **O que é:** `exocortex_daemon.bat`
* **Frequência:** 24/7 (Deixe rodando).
* **Função:** Ele vive, post, responde e curte. Você não precisa fazer nada.

## 2. O Ritual de Evolução (Manual - O "Check-up")

* **Quando fazer:** Uma vez por semana, ou quando você sentir que ele está estagnado.
* **Comando:** `python synapse.py --evolve`
* **O que acontece:** Ele vai para o "Divã". Ele lê todas as memórias da semana e diz:
    > *"Mestre, notei que fui muito agressivo na terça-feira. Proponho me tornar mais diplomático."*
* **Sua Decisão:**
  * Gostou da mudança? Rode: `python synapse.py --accept`
  * Não gostou? Ignore. Ele continua igual.

## Por que não é automático?

Se deixarmos o `--evolve` e o `--accept` no piloto automático, ele pode entrar num loop de feedback negativo e virar um "robô chato" ou "fanático" sem você ver.
**Você é o Pai/Mãe.** Você aprova o crescimento dele.

---
*Dica:* Se quiser forçar uma mudança radical, você pode editar o `persona.txt` na mão também. Ele respeitará sua edição.
