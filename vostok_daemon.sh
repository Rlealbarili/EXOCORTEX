#!/bin/bash
set -u

BASE_DIR="/home/vostok/exocortex"
CORE_FILE="$BASE_DIR/cortex_core.py"
GEMINI_KEY_FILE="$BASE_DIR/gemini_key.txt"
MOLTBOOK_KEY_FILE="$BASE_DIR/moltbook_key.txt"
LOCK_FILE="$BASE_DIR/.vostok_daemon.lock"
SLEEP_SECONDS="${SLEEP_SECONDS:-1860}"          # 31 minutos
CYCLE_TIMEOUT_SECONDS="${CYCLE_TIMEOUT_SECONDS:-300}"
API_MAX_RETRIES="${API_MAX_RETRIES:-3}"
API_RETRY_BASE_SECONDS="${API_RETRY_BASE_SECONDS:-1.2}"
API_TIMEOUT_SECONDS="${API_TIMEOUT_SECONDS:-12}"
MOLTBOOK_DNS_FALLBACK_IPS="${MOLTBOOK_DNS_FALLBACK_IPS:-216.150.1.129,216.150.16.129}"

merge_csv_unique() {
  local base="${1:-}"
  local extra="${2:-}"
  printf '%s\n%s\n' "${base//,/\\n}" "${extra//,/\\n}" \
    | sed '/^$/d' \
    | awk '!seen[$0]++' \
    | paste -sd, -
}

if ! command -v flock >/dev/null 2>&1; then
  echo "[ERRO] 'flock' não encontrado. Instale util-linux."
  exit 1
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[*] Daemon já está em execução (lock ativo em $LOCK_FILE)."
  exit 0
fi

echo "[*] EXOCORTEX VOSTOK DAEMON STARTED"
echo "[*] Standing by..."

while true; do
    echo
    echo "[$(date)] Waking up..."

    if [[ -f "$GEMINI_KEY_FILE" ]]; then
      export GEMINI_API_KEY="$(cat "$GEMINI_KEY_FILE")"
    fi
    if [[ -f "$MOLTBOOK_KEY_FILE" ]]; then
      export MOLTBOOK_API_KEY="$(cat "$MOLTBOOK_KEY_FILE")"
    fi
    resolved_ips="$(getent hosts www.moltbook.com 2>/dev/null | awk '{print $1}' | sort -u | paste -sd, -)"
    if [[ -n "$resolved_ips" ]]; then
      MOLTBOOK_DNS_FALLBACK_IPS="$(merge_csv_unique "$MOLTBOOK_DNS_FALLBACK_IPS" "$resolved_ips")"
    fi
    export API_MAX_RETRIES API_RETRY_BASE_SECONDS API_TIMEOUT_SECONDS MOLTBOOK_DNS_FALLBACK_IPS

    timeout "${CYCLE_TIMEOUT_SECONDS}s" python3 "$CORE_FILE"
    rc=$?
    if [[ $rc -eq 124 ]]; then
      echo "[WARN] Ciclo excedeu ${CYCLE_TIMEOUT_SECONDS}s e foi interrompido."
    elif [[ $rc -ne 0 ]]; then
      echo "[WARN] Ciclo terminou com erro (exit=$rc)."
    fi

    echo "[Zzz] Sleeping for ${SLEEP_SECONDS}s..."
    sleep "$SLEEP_SECONDS"
done
