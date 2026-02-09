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
