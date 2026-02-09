# Operations Runbook

## Service Lifecycle

Install and enable user service:

```bash
./ops/install_user_service.sh
```

Manual controls:

```bash
systemctl --user status petrovich.service --no-pager -l
systemctl --user restart petrovich.service
systemctl --user stop petrovich.service
systemctl --user start petrovich.service
```

Live logs:

```bash
journalctl --user -u petrovich.service -f
```

## Manual Cycle Execution

```bash
python3 cortex_core.py
```

Useful for quick diagnostics without waiting the daemon sleep window.

## Posting Safety Controls

Check state:

```bash
./petrovich_ctl.py show
```

Suspend posting:

```bash
./petrovich_ctl.py suspend --reason "maintenance"
```

Unsuspend posting:

```bash
./petrovich_ctl.py unsuspend
```

## DNS Operations

Dry-check:

```bash
./dns_repair.sh check
```

Apply fixed resolver policy:

```bash
sudo ./dns_repair.sh apply
```

## Validation Checklist

After config or deployment changes:

1. `getent hosts www.moltbook.com` returns at least one IP.
2. `curl` public endpoint returns `200`.
3. `systemctl --user status petrovich.service` is `active (running)`.
4. one cycle completes and logs `--- Fim do Ciclo ---`.
5. `./petrovich_ctl.py show` matches expected safety state.
