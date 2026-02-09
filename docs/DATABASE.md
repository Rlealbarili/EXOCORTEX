# Database

Database engine: SQLite (`memory.db`).

## Tables

## `thoughts`

- `id` (PK)
- `content`
- `source`
- `context`
- `status` (`PENDING`, `POSTED`)
- `created_at`

Purpose: store generated thoughts awaiting publication or already posted.

## `observations`

- `id` (PK)
- `content`
- `author`
- `sentiment` (reserved)
- `status`
- `created_at`

Purpose: feed-derived social context memory.

## `cycle_metrics`

- `id` (PK)
- `cycle_mode`
- `posted` (0/1)
- `network_ok` (0/1/null)
- `target_id`
- `error`
- `duration_ms`
- `created_at`

Purpose: operational telemetry for each cycle.

## `agent_state`

- `key` (PK)
- `value`
- `updated_at`

Purpose: control-plane flags, including:

- `posting_suspended`
- `posting_suspended_reason`

## `reflection_journal`

- `id` (PK)
- `topic`
- `mode` (`focus` or `explore`)
- `reflection`
- `confidence`
- `created_at`

Purpose: cognitive trace of autonomous reflection.

## `persona_versions`

- `id` (PK)
- `content`
- `source`
- `topic`
- `reflection`
- `active` (0/1)
- `created_at`

Purpose: persona evolution history with active marker.

## `mutation_events`

- `id` (PK)
- `topic`
- `decision`
- `result`
- `created_at`

Purpose: controlled record of self-modification attempts.
