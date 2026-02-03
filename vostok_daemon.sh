#!/bin/bash
# EXOCORTEX VOSTOK DAEMON
# Interval: 35 Minutes (Chronological Sync)

echo "[*] EXOCORTEX VOSTOK DAEMON STARTED"
echo "[*] Standing by..."

while true; do
    echo ""
    echo "[$(date)] Waking up..."
    # Ensure API Key is available
    export GEMINI_API_KEY="REVOKED_GOOGLE_API_KEY"
    python3 /home/vostok/exocortex/cortex_core.py
    echo "[Zzz] Sleeping for 35 minutes..."
    sleep 2100
done
