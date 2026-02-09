#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/vostok/exocortex"
SERVICE_SRC="$BASE_DIR/ops/petrovich.service"
SERVICE_DST="$HOME/.config/systemd/user/petrovich.service"

mkdir -p "$HOME/.config/systemd/user"
cp "$SERVICE_SRC" "$SERVICE_DST"

systemctl --user daemon-reload
systemctl --user enable --now petrovich.service

echo "[OK] Serviço petrovich habilitado no systemd --user"
systemctl --user status petrovich.service --no-pager | sed -n '1,40p'
