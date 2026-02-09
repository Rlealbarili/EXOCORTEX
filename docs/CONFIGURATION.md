# Configuration

## Runtime Prerequisites

- Linux host with `systemd --user`
- Python 3.10+ recommended
- `psutil` package
- `google-generativeai` package (for LLM features)
- network access to `https://www.moltbook.com/api/v1`

## Secrets

The project reads keys in this order:

1. environment variables
2. local key files in repository root

Keys:

- `MOLTBOOK_API_KEY` or `moltbook_key.txt`
- `GEMINI_API_KEY` or `gemini_key.txt`

Never commit key files.

## Environment Variables

## Core API

- `API_TIMEOUT_SECONDS` (default: `12`)
- `API_MAX_RETRIES` (default: `3`)
- `API_RETRY_BASE_SECONDS` (default: `1.2`)
- `MOLTBOOK_DNS_FALLBACK_IPS` (default in daemon: `216.150.1.129,216.150.16.129`)

## Cycle / Modules

- `MODULE_TIMEOUT_SECONDS` (default: `6`)
- `ENABLED_MODULES` (comma-separated module filenames)
- `SLEEP_SECONDS` (daemon default: `1860`)
- `CYCLE_TIMEOUT_SECONDS` (daemon default: `300`)

## Cognition / Mutation

- `GEMINI_TIMEOUT_SECONDS` (default: `25`)
- `AUTONOMOUS_MUTATION_ENABLED` (`0` or `1`, default: `0`)
- `MUTATION_RATE` (default: `0.08`)

## Safety

- `AUTO_UNSUSPEND_ON_STATUS_CLAIMED` (default: `0`)

Recommended: keep `0` and unsuspend manually with `petrovich_ctl.py`.

## Files

- `persona.txt`: current active persona
- `interests.json`: weighted reflection topic strategy
- `memory.db`: runtime memory/state store
