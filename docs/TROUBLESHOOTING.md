# Troubleshooting

## Symptom: `Temporary failure in name resolution`

Likely cause:

- local resolver instability or upstream DNS path issues

Actions:

1. check resolution:
   ```bash
   getent hosts www.moltbook.com
   ```
2. apply resolver policy:
   ```bash
   sudo ./dns_repair.sh apply
   ```
3. restart service:
   ```bash
   systemctl --user restart petrovich.service
   ```
4. verify fallback is active in daemon logs.

## Symptom: API `401/403` with suspended account

Cause:

- platform-level enforcement from Moltbook

Behavior:

- project sets `posting_suspended=1` and enters safe observe mode

Action:

- wait until suspension expires
- clear safety flag manually:
  ```bash
  ./petrovich_ctl.py unsuspend
  ```

## Symptom: Cycle hangs too long

Cause:

- slow external call (module or LLM)

Actions:

- verify `CYCLE_TIMEOUT_SECONDS` in daemon config
- verify `MODULE_TIMEOUT_SECONDS`
- reduce `GEMINI_TIMEOUT_SECONDS` if needed

## Symptom: No posts despite healthy service

Check:

1. `./petrovich_ctl.py show` for `posting_suspended`
2. Moltbook API status endpoint behavior
3. `cortex.log` for rate limit (`429`) or auth errors

## Symptom: LLM unavailable

Cause:

- missing or invalid `GEMINI_API_KEY`

Behavior:

- system falls back to non-LLM thought generation path

Action:

- validate key file/env and rerun one cycle manually.
