#!/bin/bash
# EXOCORTEX VOSTOK DAEMON
# Interval: 35 Minutes (Chronological Sync)
# SECURITY: API Key is loaded from external file (never committed to Git)

echo "[*] EXOCORTEX VOSTOK DAEMON STARTED"
echo "[*] Standing by..."

while true; do
    echo ""
    echo "[$(date)] Waking up..."
    # Load API Key from external file (gemini_key.txt is in .gitignore)
    export GEMINI_API_KEY=$(cat /home/vostok/exocortex/gemini_key.txt)
    python3 /home/vostok/exocortex/cortex_core.py
    echo "[Zzz] Sleeping for 35 minutes..."
    sleep 2100
done
