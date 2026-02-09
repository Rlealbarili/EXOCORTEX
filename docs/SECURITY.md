# Security

## Secret Management

- API keys must be provided by environment variables or local key files.
- Key files (`gemini_key.txt`, `moltbook_key.txt`) are ignored by git.
- Never log raw secrets or include them in issue reports.
- Install repository hooks to block accidental secret commits:
  ```bash
  ./scripts/install_hooks.sh
  ```
- Run local secret scans before pushing:
  ```bash
  ./scripts/secret_scan.sh head
  ./scripts/secret_scan.sh history
  ```

## Network Safety

- API calls use timeout, retries, and bounded backoff.
- DNS fallback is restricted to the Moltbook API host context.
- Service runs in user scope, not as root.

## Operational Safety

- Posting can be hard-paused by state (`posting_suspended=1`).
- Suspension responses from API automatically trigger posting pause.
- Unsuspend is manual by default to avoid accidental policy violations.

## Mutation Controls

- Autonomous code mutation is disabled by default (`AUTONOMOUS_MUTATION_ENABLED=0`).
- Mutation attempts are recorded in `mutation_events`.
- Enable only in controlled experiments.

## Recommended Hardening

1. move keys to a secret manager (or systemd user environment drop-in).
2. enforce file permissions on key files (`chmod 600`).
3. add outbound firewall rules restricted to required destinations.
4. include regular backups for `memory.db`.
