# Development Guide

## Local Setup

1. install Python dependencies:
   - `psutil`
   - `google-generativeai`
2. create local key files or set env vars:
   - `gemini_key.txt`
   - `moltbook_key.txt`
3. run one cycle:
   ```bash
   python3 cortex_core.py
   ```

## Code Layout

- `cortex_core.py`: orchestrator and API/state logic
- `vostok_synapse.py`: cognition and generation
- `exocortex_modules/`: sensory modules
- `ops/`: service installation assets
- `docs/`: official project documentation

## Safe Change Workflow

1. make small scoped changes.
2. install hooks once per clone:
   ```bash
   ./scripts/install_hooks.sh
   ```
3. run syntax check:
   ```bash
   python3 -m py_compile cortex_core.py vostok_synapse.py exocortex_modules/*.py
   ```
4. run secret scan:
   ```bash
   ./scripts/secret_scan.sh head
   ```
5. run one manual cycle:
   ```bash
   python3 cortex_core.py
   ```
6. if daemonized, restart user service:
   ```bash
   systemctl --user restart petrovich.service
   ```
7. inspect logs for regressions.

## Commit Hygiene

- do not commit runtime artifacts (`*.log`, `memory.db`, lock files).
- do not commit secrets.
- keep operational changes and functional code changes traceable in commit messages.

## Release Checklist

1. docs updated for any behavior/config changes.
2. service starts cleanly after restart.
3. safety controls validated (`petrovich_ctl.py show`).
4. DNS check passes (`getent hosts www.moltbook.com`).
5. a full cycle finishes within expected timeout.
