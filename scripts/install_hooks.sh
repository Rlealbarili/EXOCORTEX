#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
chmod +x scripts/secret_scan.sh

echo "[ok] Git hooks installed (core.hooksPath=.githooks)"
