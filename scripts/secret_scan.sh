#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-head}"

# High-signal patterns for accidental secret exposure.
PATTERN='(AIza[0-9A-Za-z_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{10,})'

scan_head() {
  echo "[scan] working tree + index"
  # Search tracked and untracked text files in repository tree.
  if rg -n -S -g '!*.png' -g '!*.jpg' -g '!*.jpeg' -g '!*.gif' -g '!*.pdf' "$PATTERN" .; then
    return 1
  fi
  return 0
}

scan_history() {
  echo "[scan] full git history"
  local found=0
  while read -r commit; do
    if git grep -nEI "$PATTERN" "$commit" >/tmp/secret_scan_matches.out 2>/dev/null; then
      echo "commit: $commit"
      cat /tmp/secret_scan_matches.out
      found=1
    fi
  done < <(git rev-list --all)
  rm -f /tmp/secret_scan_matches.out
  [[ $found -eq 0 ]]
}

case "$MODE" in
  head)
    scan_head
    ;;
  history)
    scan_history
    ;;
  all)
    scan_head && scan_history
    ;;
  *)
    echo "Usage: $0 [head|history|all]"
    exit 2
    ;;
esac

echo "[ok] no secrets found for mode: $MODE"
