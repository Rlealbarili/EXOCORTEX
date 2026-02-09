#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"
RESOLVED_CONF="/etc/systemd/resolved.conf"

check_dns() {
  echo "[*] /etc/resolv.conf -> $(readlink -f /etc/resolv.conf || true)"
  echo "[*] Conteúdo atual de /etc/resolv.conf:"
  cat /etc/resolv.conf || true
  echo
  echo "[*] Teste DNS (www.moltbook.com):"
  getent hosts www.moltbook.com || true
}

apply_dns() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "[ERRO] Rode com sudo: sudo ./dns_repair.sh apply"
    exit 1
  fi

  cp -a "$RESOLVED_CONF" "${RESOLVED_CONF}.bak.$(date +%Y%m%d%H%M%S)"
  cat > "$RESOLVED_CONF" <<'EOF'
[Resolve]
DNS=1.1.1.1 8.8.8.8
FallbackDNS=1.0.0.1 8.8.4.4
Domains=~.
DNSSEC=no
MulticastDNS=no
LLMNR=no
Cache=yes
DNSStubListener=yes
EOF

  systemctl restart systemd-resolved
  sleep 1
  echo "[*] DNS aplicado. Status:"
  resolvectl status || true
  echo "[*] Teste final:"
  getent hosts www.moltbook.com || true
}

case "$MODE" in
  check)
    check_dns
    ;;
  apply)
    apply_dns
    ;;
  *)
    echo "Uso: $0 [check|apply]"
    exit 1
    ;;
esac
