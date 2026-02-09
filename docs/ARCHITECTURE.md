# Architecture

## Overview

Exocortex Petrovich is a single-node autonomous agent system with:

- cycle orchestration (`cortex_core.py`)
- cognitive and generation layer (`vostok_synapse.py`)
- sensory extensions (`exocortex_modules/*.py`)
- operational controls (`petrovich_ctl.py`, `vostok_daemon.sh`)
- local persistence (`memory.db`)

## Runtime Model

1. `vostok_daemon.sh` wakes up every `SLEEP_SECONDS`.
2. One cycle is executed with timeout protection (`CYCLE_TIMEOUT_SECONDS`).
3. `cortex_core.py`:
   - scans feed and stores observations
   - refreshes account status
   - runs sensory modules
   - invokes cognitive loop
   - decides between observe/reply/post
   - records cycle metrics
4. State and memory are persisted in SQLite.

## Core Components

## `cortex_core.py`

- API client with:
  - timeout, retries, backoff
  - DNS failure detection
  - optional IP fallback for `www.moltbook.com`
- memory/state management:
  - thoughts, observations, cycle metrics
  - agent state flags (for example `posting_suspended`)
- cycle mode arbitration:
  - `observe_only`
  - `social_reply`
  - `autonomous_post`

## `vostok_synapse.py`

- persona loading and updates (`persona.txt`)
- cognitive loop with topic selection from `interests.json`
- reflection persistence and persona versioning
- optional mutation execution (`run_builder`)
- LLM-backed text generation with timeout guard
- rule-based + LLM fallback verification solver

## Sensory Modules (`exocortex_modules/`)

- `atualizador.py`: placeholder updater module
- `codigo_otimizador.py`: code analysis simulation
- `entropia_monitor.py`: entropy snapshot
- `latency_analyzer.py`: latency probe
- `recursos_gerenciador.py`: CPU/MEM/DISK snapshot

Modules are launched as subprocesses and their last output line becomes sensory context.

## Service Layer

- `ops/petrovich.service`: user-level systemd service unit
- `ops/install_user_service.sh`: installs and enables service
- `vostok_daemon.sh`: lock-protected daemon loop (`flock`)

## Control Plane

- `petrovich_ctl.py`: operational state toggles
  - `show`
  - `suspend --reason ...`
  - `unsuspend`

## Data Flow

1. Feed observations -> `observations`
2. Thought generation -> `thoughts` with `PENDING`
3. Successful post -> thought marked `POSTED`
4. Reflection/persona updates -> cognitive tables
5. Cycle telemetry -> `cycle_metrics`
6. Safety states -> `agent_state`

## Safety Model

- posting can be force-paused via `agent_state.posting_suspended=1`
- account suspension responses (`401/403`) auto-set safety pause
- optional auto-unsuspend on `claimed` status is disabled by default
